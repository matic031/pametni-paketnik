package com.example.pametnipaketnik.network

import android.content.Context
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {
    private const val BASE_URL = "http://10.0.2.2:3000/" // Prilagoid

    private var apiService: ApiService? = null

    fun getApiService(context: Context): ApiService {
        if (apiService == null) {
            // Interceptor za logiranje
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }

            val authInterceptor = AuthInterceptor(context.applicationContext)

            // Sestavimo OkHttpClient z obema interceptorjema
            val okHttpClient = OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .addInterceptor(authInterceptor) // Dodamo auth interceptor
                .build()

            // Sestavimo Retrofit
            val retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(okHttpClient) // Uporabimo novi client
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            apiService = retrofit.create(ApiService::class.java)
        }
        return apiService!!
    }
}