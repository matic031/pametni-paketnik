package com.example.pametnipaketnik.network

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Context
import android.content.Intent
import com.example.pametnipaketnik.LoginActivity
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {
    private const val BASE_URL = "http://10.0.2.2:3000/"

    private var apiService: ApiService? = null

    // Create a shared logging interceptor
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    // Create the OkHttpClient for the lazy api property
    private val httpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .addInterceptor { chain ->
            val request = chain.request()
            val response = chain.proceed(request)

            if (response.code == 401) {
                AuthManager.handleAuthFailure()
            }
            response
        }
        .build()

    fun getApiService(context: Context): ApiService {
        if (apiService == null) {
            val authInterceptor = AuthInterceptor(context.applicationContext)

            // Build OkHttpClient with both interceptors
            val okHttpClient = OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .addInterceptor(authInterceptor)
                .build()

            // Build Retrofit
            val retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            apiService = retrofit.create(ApiService::class.java)
        }
        return apiService!!
    }

    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }

    @SuppressLint("StaticFieldLeak")
    object AuthManager {
        private var currentActivity: Activity? = null

        fun setCurrentActivity(activity: Activity) {
            currentActivity = activity
        }

        fun needsFaceRegistration(context: Context): Boolean {
            val sharedPreferences = context.getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
            val token = sharedPreferences.getString("AUTH_TOKEN", null)
            val faceRegistered = sharedPreferences.getBoolean("FACE_REGISTERED", false)

            return !token.isNullOrEmpty() && !faceRegistered
        }

        fun hasTokenButNeedsFaceVerification(context: Context): Boolean {
            val sharedPreferences = context.getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
            val token = sharedPreferences.getString("AUTH_TOKEN", null)
            val faceRegistered = sharedPreferences.getBoolean("FACE_REGISTERED", false)
            val faceVerified = sharedPreferences.getBoolean("FACE_VERIFIED", false)

            return !token.isNullOrEmpty() && faceRegistered && !faceVerified
        }

        fun syncUserStatus(context: Context, faceRegistered: Boolean) {
            val sharedPreferences = context.getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
            with(sharedPreferences.edit()) {
                putBoolean("FACE_REGISTERED", faceRegistered)
                apply()
            }
        }

        fun isLoggedIn(context: Context): Boolean {
            val sharedPreferences = context.getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
            val token = sharedPreferences.getString("AUTH_TOKEN", null)
            val faceVerified = sharedPreferences.getBoolean("FACE_VERIFIED", false)

            return !token.isNullOrEmpty() && faceVerified
        }

        fun handleAuthFailure() {
            currentActivity?.let { activity ->
                // Clear auth token and face verification status
                val sharedPreferences = activity.getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
                with(sharedPreferences.edit()) {
                    remove("AUTH_TOKEN")
                    remove("FACE_VERIFIED")
                    apply()
                }

                val intent = Intent(activity, LoginActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                activity.startActivity(intent)
                activity.finish()
            }
        }

        fun logout(context: Context) {
            val sharedPreferences = context.getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
            with(sharedPreferences.edit()) {
                remove("AUTH_TOKEN")
                remove("FACE_VERIFIED")
                apply()
            }

            val intent = Intent(context, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            context.startActivity(intent)
        }
    }
}