package com.example.pametnipaketnik.ui.login

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.pametnipaketnik.data.ApiErrorResponse
import com.example.pametnipaketnik.data.LoginRequest
import com.example.pametnipaketnik.data.LoginResponse
import com.example.pametnipaketnik.network.RetrofitInstance
import com.google.gson.Gson
import kotlinx.coroutines.launch

sealed class LoginResult {
    object Loading : LoginResult()
    data class Success(val response: LoginResponse) : LoginResult()
    data class Error(val message: String) : LoginResult()
    data class FaceVerificationRequired(val message: String, val userId: String) : LoginResult()
}

class LoginViewModel(application: Application) : AndroidViewModel(application) {

    private val _loginResult = MutableLiveData<LoginResult>()
    val loginResult: LiveData<LoginResult> = _loginResult

    fun loginUser(username: String, password: String) {
        if (username.isEmpty() || password.isEmpty()) {
            _loginResult.value = LoginResult.Error("Username and password are required")
            return
        }

        _loginResult.value = LoginResult.Loading
        viewModelScope.launch {
            try {
                val loginRequest = LoginRequest(username, password)
                val response = RetrofitInstance.getApiService(getApplication()).loginUser(LoginRequest(username, password))

                if (response.isSuccessful && response.body() != null) {
                    val loginResponse = response.body()!!
                    if (loginResponse.success) {
                        _loginResult.value = LoginResult.Success(loginResponse)
                    } else {
                        _loginResult.value = LoginResult.Error(loginResponse.message ?: "Unknown login error")
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = if (errorBody != null) {
                        try {
                            val loginResponse = Gson().fromJson(errorBody, LoginResponse::class.java)
                            // čekira ali je potrebna verifikacija obraza
                            if (response.code() == 403 && loginResponse.requiresFaceVerification == true) {
                                _loginResult.value = LoginResult.FaceVerificationRequired(
                                    loginResponse.message ?: "Potrebna je ponovna verifikacija obraza",
                                    loginResponse.userId ?: ""
                                )
                                return@launch
                            } else {
                                loginResponse.message ?: "Login failed"
                            }
                        } catch (e: Exception) {
                            try {
                                val apiError = Gson().fromJson(errorBody, ApiErrorResponse::class.java)
                                apiError.message ?: "Login failed"
                            } catch (e2: Exception) {
                                "Error: $errorBody"
                            }
                        }
                    } else {
                        "Login failed with code: ${response.code()}"
                    }
                    _loginResult.value = LoginResult.Error(errorMessage)
                }
            } catch (e: Exception) {
                _loginResult.value = LoginResult.Error("Network error: ${e.message}")
            }
        }
    }
}