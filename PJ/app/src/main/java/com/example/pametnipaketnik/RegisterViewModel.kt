package com.example.pametnipaketnik

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.pametnipaketnik.data.ApiErrorResponse
import com.example.pametnipaketnik.network.RetrofitInstance
import com.google.gson.Gson
import kotlinx.coroutines.launch

sealed class RegisterResult {
    object Loading : RegisterResult()
    data class Success(val message: String) : RegisterResult()
    data class Error(val message: String) : RegisterResult()
}

class RegisterViewModel : ViewModel() {

    private val _registerResult = MutableLiveData<RegisterResult>()
    val registerResult: LiveData<RegisterResult> = _registerResult

    fun registerUser(username: String, email: String, password: String) {
        _registerResult.value = RegisterResult.Loading

        viewModelScope.launch {
            try {
                val registerRequest = RegisterRequest(username, email, password)
                val response = RetrofitInstance.api.registerUser(registerRequest)

                if (response.isSuccessful && response.body() != null) {
                    val registerResponse = response.body()!!
                    if (registerResponse.success) {
                        _registerResult.value = RegisterResult.Success(registerResponse.message ?: "Registracija uspešna")
                    } else {
                        _registerResult.value = RegisterResult.Error(registerResponse.message ?: "Registracija ni uspela")
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = if (errorBody != null) {
                        try {
                            val apiError = Gson().fromJson(errorBody, ApiErrorResponse::class.java)
                            apiError.message ?: "Registration failed"
                        } catch (e: Exception) {
                            "Error: $errorBody"
                        }
                    } else {
                        "Registration failed with code: ${response.code()}"
                    }
                    _registerResult.value = RegisterResult.Error(errorMessage)
                }
            } catch (e: Exception) {
                _registerResult.value = RegisterResult.Error("Network error: ${e.message}")
            }
        }
    }
}