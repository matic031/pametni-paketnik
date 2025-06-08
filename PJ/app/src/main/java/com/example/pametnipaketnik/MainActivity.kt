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
import kotlinx.coroutines.launch
import kotlin.apply
import kotlin.or

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
        val faceRegistered = sharedPreferences.getBoolean("FACE_REGISTERED", false)
        val faceVerified = sharedPreferences.getBoolean("FACE_VERIFIED", false)

        if (token == null) {
            Log.d(TAG, "checkAuthAndRedirect: No token, redirecting to login")
            navigateToLogin()
            return
        }

        lifecycleScope.launch {
            try {
                val response = RetrofitInstance.api.getCurrentUserProfile(token)
                if (response.isSuccessful && response.body() != null) {
                    val userResponse = response.body()!!
                    if (userResponse.success) {
                        val userId = userResponse.user.id
                        with(sharedPreferences.edit()) {
                            putString("USER_ID", userId)
                            apply()
                        }

                        val userFaceRegistered = userResponse.user.faceRegistered
                        RetrofitInstance.AuthManager.syncUserStatus(this@MainActivity, userFaceRegistered)

                        if (!userFaceRegistered) {
                            Log.d(TAG, "checkAuthAndRedirect: Face not registered, redirecting to registration")
                            navigateToFaceRegistration()
                        } else if (!faceVerified) {
                            Log.d(TAG, "checkAuthAndRedirect: Face registered but not verified, redirecting to verification")
                            navigateToFaceVerification()
                        }
                    } else {
                        Log.d(TAG, "checkAuthAndRedirect: Failed to get user profile, redirecting to login")
                        navigateToLogin()
                    }
                } else {
                    Log.d(TAG, "checkAuthAndRedirect: API error, redirecting to login")
                    navigateToLogin()
                }
            } catch (e: Exception) {
                Log.e(TAG, "checkAuthAndRedirect: Exception", e)
                navigateToLogin()
            }
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