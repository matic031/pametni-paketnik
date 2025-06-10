package com.example.pametnipaketnik

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.example.pametnipaketnik.databinding.ActivityMainBinding
import com.example.pametnipaketnik.network.RetrofitInstance
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val TAG = "MainActivity"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate: Checking authentication status")

        RetrofitInstance.AuthManager.setCurrentActivity(this)

        checkAuthAndRedirect()

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val navView = binding.navView
        val navController = findNavController(R.id.nav_host_fragment_activity_main)
        val appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.navigation_home, R.id.navigation_dashboard, R.id.navigation_notifications,
                R.id.navigation_profile
            )
        )
        setupActionBarWithNavController(navController, appBarConfiguration)
        navView.setupWithNavController(navController)
    }

    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume: Checking authentication status")
        checkAuthAndRedirect()
    }

    private fun checkAuthAndRedirect() {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        val token = sharedPreferences.getString("AUTH_TOKEN", null)
        if (!token.isNullOrEmpty()) {
            lifecycleScope.launch {
                try {
                    val response = withContext(Dispatchers.IO) {
                        RetrofitInstance.getApiService(this@MainActivity)
                            .getCurrentUserProfile("Bearer $token")
                    }
                    if (response.isSuccessful && response.body() != null) {
                        val user = response.body()!!.user
                        val lastFaceVerification = response.body()!!.user.lastFaceVerification
                        with(sharedPreferences.edit()) {
                            putString("USER_ID", user.id)
                            putString("USER_EMAIL", user.email)
                            putString("USER_USERNAME", user.username)
                            putString("USER_NAME", user.name ?: "")
                            putString("USER_LASTNAME", user.lastName ?: "")
                            putBoolean("USER_IS_ADMIN", user.isAdmin)
                            putBoolean("FACE_REGISTERED", user.faceRegistered)
                            putString("LAST_FACE_VERIFICATION", lastFaceVerification)
                            putBoolean("FACE_VERIFIED", isFaceVerified(lastFaceVerification))
                            apply()
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to fetch user profile: ${e.message}")
                }
                continueAuthCheck()
            }
        } else {
            continueAuthCheck()
        }
    }

    private fun isFaceVerified(lastFaceVerification: String?): Boolean {
        if (lastFaceVerification.isNullOrEmpty()) return false
        return try {
            val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX", Locale.getDefault())
            val lastDate = sdf.parse(lastFaceVerification)
            val now = Date()
            val diffMillis = now.time - (lastDate?.time ?: 0L)
            val diffHours = TimeUnit.MILLISECONDS.toHours(diffMillis)
            diffHours < 2
        } catch (e: Exception) {
            false
        }
    }

    private fun continueAuthCheck() {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        val token = sharedPreferences.getString("AUTH_TOKEN", null)
        val faceRegistered = sharedPreferences.getBoolean("FACE_REGISTERED", false)
        val faceVerified = sharedPreferences.getBoolean("FACE_VERIFIED", false)
        val email = sharedPreferences.getString("USER_EMAIL", "unknown")
        Log.d(TAG, "checkAuthAndRedirect: faceRegistered=$faceRegistered, faceVerified=$faceVerified, email=$email, token=$token")
        when {
            token.isNullOrEmpty() -> navigateToLogin()
            !faceRegistered -> navigateToFaceRegistration()
            faceRegistered && !faceVerified -> navigateToFaceVerification()
        }
    }

    private fun navigateToLogin() {
        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }

    private fun navigateToFaceRegistration() {
        val intent = Intent(this, FaceRegistrationActivity::class.java)
        startActivity(intent)
        finish()
    }

    private fun navigateToFaceVerification() {
        val intent = Intent(this, FaceVerificationActivity::class.java)
        startActivity(intent)
        finish()
    }
}