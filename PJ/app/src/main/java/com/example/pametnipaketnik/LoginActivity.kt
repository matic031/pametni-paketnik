package com.example.pametnipaketnik

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import com.example.pametnipaketnik.data.TokenManager
import com.example.pametnipaketnik.databinding.ActivityLoginBinding
import com.example.pametnipaketnik.network.RetrofitInstance
import com.example.pametnipaketnik.ui.login.LoginResult
import com.example.pametnipaketnik.ui.login.LoginViewModel

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private val loginViewModel: LoginViewModel by viewModels()    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (isUserLoggedIn()) {
            navigateToMainActivity()
            return
        }
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        createNotificationChannel()
        checkIfUserIsLoggedIn()

        binding.buttonLogin.setOnClickListener {
            binding.textViewError.visibility = View.GONE
            val username = binding.editTextUsername.text.toString().trim()
            val password = binding.editTextPassword.text.toString().trim()
            loginViewModel.loginUser(username, password)
        }

        binding.textViewRegisterLink.setOnClickListener {
            val intent = Intent(this, RegisterActivity::class.java)
            startActivity(intent)
        }

        observeViewModel()
    }

    private fun checkIfUserIsLoggedIn() {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        val token = sharedPreferences.getString("AUTH_TOKEN", null)
        if (token != null && token.startsWith("Bearer ")) {
            navigateToMainActivity()
        }
    }

    private fun isUserLoggedIn(): Boolean {
        return TokenManager.getToken(this) != null
    }

    private fun observeViewModel() {
        loginViewModel.loginResult.observe(this) { result ->
            when (result) {
                is LoginResult.Loading -> {
                    binding.progressBarLogin.visibility = View.VISIBLE
                    binding.buttonLogin.isEnabled = false
                    binding.textViewError.visibility = View.GONE
                }
                is LoginResult.Success -> {
                    binding.progressBarLogin.visibility = View.GONE
                    binding.buttonLogin.isEnabled = true
                    binding.textViewError.visibility = View.GONE

                    val tokenToSave = result.response.token
                    saveAuthToken(tokenToSave)
                    // Shranimo žeton v TokenManager
                    TokenManager.saveToken(this, result.response.token)

                    result.response.user?.id?.let { userId ->
                        saveUserId(userId)
                    }

                    val faceRegistered = result.response.faceRegistered
                    val lastFaceVerification = result.response.lastFaceVerification

                    val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
                    with(sharedPreferences.edit()) {
                        putBoolean("FACE_REGISTERED", faceRegistered)
                        putString("LAST_FACE_VERIFICATION", lastFaceVerification)
                        apply()
                    }

                    result.response.user?.let { user ->
                        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
                        with(sharedPreferences.edit()) {
                            putString("USER_ID", user.id)
                            putString("USER_EMAIL", user.email)
                            putString("USER_USERNAME", user.username)
                            putString("USER_NAME", user.name ?: "")
                            putString("USER_LASTNAME", user.lastName ?: "")
                            putBoolean("USER_IS_ADMIN", user.isAdmin)
                            apply()
                        }
                    }

                    Log.d("LoginActivity", "Face registered: $faceRegistered")

                    RetrofitInstance.AuthManager.syncUserStatus(this, faceRegistered)

                    if (faceRegistered) {
                        navigateToFaceVerification()
                    } else {
                        navigateToFaceRegistration()
                    }

                }
                is LoginResult.Error -> {
                    binding.progressBarLogin.visibility = View.GONE
                    binding.buttonLogin.isEnabled = true
                    binding.textViewError.text = result.message
                    binding.textViewError.visibility = View.VISIBLE

                    binding.editTextUsername.text?.clear()
                    binding.editTextPassword.text?.clear()
                    binding.editTextUsername.requestFocus()
                }
                is LoginResult.FaceVerificationRequired -> {
                    binding.progressBarLogin.visibility = View.GONE
                    binding.buttonLogin.isEnabled = true
                    
                    showFaceVerificationNotification(result.message)
                    
                    binding.textViewError.text = result.message
                    binding.textViewError.visibility = View.VISIBLE

                    binding.editTextUsername.text?.clear()
                    binding.editTextPassword.text?.clear()
                    binding.editTextUsername.requestFocus()
                }
            }
        }
    }

    private fun saveUserId(userId: String) {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        with(sharedPreferences.edit()) {
            putString("USER_ID", userId)
            apply()
        }
    }

    private fun saveAuthToken(token: String) {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        with(sharedPreferences.edit()) {
            putString("AUTH_TOKEN", token)
            apply()
        }
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

    private fun navigateToMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Verifikacija obraza"
            val descriptionText = "Obvestila za verifikacijo obraza"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel("FACE_VERIFICATION_CHANNEL", name, importance).apply {
                description = descriptionText
            }
            val notificationManager: NotificationManager =
                getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun showFaceVerificationNotification(message: String) {
        val builder = NotificationCompat.Builder(this, "FACE_VERIFICATION_CHANNEL")
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle("Verifikacija obraza potrebna")
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)

        val notificationManager: NotificationManager =
            getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(1001, builder.build())
    }
}