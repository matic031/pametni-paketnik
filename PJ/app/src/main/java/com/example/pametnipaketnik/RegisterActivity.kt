package com.example.pametnipaketnik

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.example.pametnipaketnik.databinding.ActivityRegisterBinding

class RegisterActivity : AppCompatActivity() {

    private lateinit var binding: ActivityRegisterBinding
    private lateinit var viewModel: RegisterViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this)[RegisterViewModel::class.java]

        binding.buttonRegister.setOnClickListener {
            val username = binding.editTextUsername.text.toString().trim()
            val email = binding.editTextEmail.text.toString().trim()
            val password = binding.editTextPassword.text.toString().trim()
            val confirmPassword = binding.editTextConfirmPassword.text.toString().trim()

            if (validateInputs(username, email, password, confirmPassword)) {
                viewModel.registerUser(username, email, password)
            }
        }

        binding.textViewLoginLink.setOnClickListener {
            finish() // Go back to LoginActivity
        }

        observeViewModel()
    }

    private fun validateInputs(username: String, email: String, password: String, confirmPassword: String): Boolean {
        if (username.isEmpty()) {
            showError("Username is required")
            return false
        }
        if (email.isEmpty()) {
            showError("Email is required")
            return false
        }
        if (password.isEmpty()) {
            showError("Password is required")
            return false
        }
        if (password != confirmPassword) {
            showError("Passwords do not match")
            return false
        }
        return true
    }

    private fun observeViewModel() {
        viewModel.registerResult.observe(this) { result ->
            when (result) {
                is RegisterResult.Loading -> {
                    binding.progressBarRegister.visibility = View.VISIBLE
                    binding.buttonRegister.isEnabled = false
                    binding.textViewError.visibility = View.GONE
                }
                is RegisterResult.Success -> {
                    binding.progressBarRegister.visibility = View.GONE
                    Toast.makeText(this, "Registracija uspešna", Toast.LENGTH_LONG).show()
                    finish()
                }
                is RegisterResult.Error -> {
                    binding.progressBarRegister.visibility = View.GONE
                    binding.buttonRegister.isEnabled = true
                    showError(result.message)
                }
            }
        }
    }

    private fun showError(message: String) {
        binding.textViewError.text = message
        binding.textViewError.visibility = View.VISIBLE
    }
}