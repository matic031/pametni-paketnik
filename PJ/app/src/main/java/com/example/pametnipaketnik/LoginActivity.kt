package com.example.pametnipaketnik

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.example.pametnipaketnik.databinding.ActivityLoginBinding
import com.example.pametnipaketnik.ui.login.LoginResult
import com.example.pametnipaketnik.ui.login.LoginViewModel
import com.example.pametnipaketnik.network.RetrofitInstance

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private val loginViewModel: LoginViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

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

                    result.response.user?.id?.let { userId ->
                        saveUserId(userId)
                    }

                    val faceRegistered = result.response.user?.faceRegistered ?: false

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
}