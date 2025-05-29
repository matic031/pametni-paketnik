package com.example.pametnipaketnik

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.example.pametnipaketnik.MainActivity
import com.example.pametnipaketnik.databinding.ActivityLoginBinding
import com.example.pametnipaketnik.ui.login.LoginResult
import com.example.pametnipaketnik.ui.login.LoginViewModel

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

        binding.textViewRegisterLink.setOnClickListener{
            val registerUrl = "http://10.0.2.2:5173/register" // URL za registracij0

            val finalUrl = if (isEmulator()) {
                registerUrl.replace("localhost", "10.0.2.2")
            } else {
               registerUrl
            }

            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(finalUrl))
                startActivity(intent)
            } catch (e: Exception) {
                // V primeru, da ni nameščenega brskalnika ali pride do druge napake
                Toast.makeText(this, "Ne morem odpreti povezave za registracijo.", Toast.LENGTH_SHORT).show()
                e.printStackTrace()
            }
        }

        observeViewModel()
    }

    private fun isEmulator(): Boolean {
        return (android.os.Build.FINGERPRINT.startsWith("generic")
                || android.os.Build.FINGERPRINT.startsWith("unknown")
                || android.os.Build.MODEL.contains("google_sdk")
                || android.os.Build.MODEL.contains("Emulator")
                || android.os.Build.MODEL.contains("Android SDK built for x86")
                || android.os.Build.MANUFACTURER.contains("Genymotion")
                || (android.os.Build.BRAND.startsWith("generic") && android.os.Build.DEVICE.startsWith("generic"))
                || "google_sdk" == android.os.Build.PRODUCT)
    }

    private fun checkIfUserIsLoggedIn() {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        val token = sharedPreferences.getString("AUTH_TOKEN", null)
        if (token != null && token.startsWith("Bearer ")) { // Preverimo, če žeton obstaja in je v pričakovani obliki
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
                    // Uporabimo sporočilo iz API odgovora, če obstaja
                    Toast.makeText(this, result.response.message ?: "Prijava uspešna!", Toast.LENGTH_LONG).show()

                    val tokenToSave = result.response.token // Shranimo celoten "Bearer <token>"
                    // val tokenToSave = result.response.token.removePrefix("Bearer ").trim()
                    saveAuthToken(tokenToSave)

                    navigateToMainActivity()
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

    private fun saveAuthToken(token: String) {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        with(sharedPreferences.edit()) {
            putString("AUTH_TOKEN", token) // Shranjujemo celoten "Bearer <token>"
            apply()
        }
    }

    private fun navigateToMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        // intent.putExtra("USER_USERNAME", loginViewModel.loginResult.value?.let { if (it is LoginResult.Success) it.response.user?.username else null })
        startActivity(intent)
        finish()
    }
}