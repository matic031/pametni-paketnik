package com.example.pametnipaketnik.ui.login

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.pametnipaketnik.data.LoginRequest
import com.example.pametnipaketnik.data.LoginResponse
import com.example.pametnipaketnik.network.RetrofitInstance
import com.google.gson.Gson
import kotlinx.coroutines.launch
import com.example.pametnipaketnik.data.ApiErrorResponse


sealed class LoginResult {
    data class Success(val response: LoginResponse) : LoginResult() // Vrača celoten LoginResponse
    data class Error(val message: String) : LoginResult()
    object Loading : LoginResult()
}

class LoginViewModel(application: Application) : AndroidViewModel(application) {

    private val _loginResult = MutableLiveData<LoginResult>()
    val loginResult: LiveData<LoginResult> = _loginResult

    fun loginUser(username: String, password: String) {
        if (username.isBlank() || password.isBlank()) {
            _loginResult.value = LoginResult.Error("Uporabniško ime in geslo ne smeta biti prazna.")
            return
        }

        _loginResult.value = LoginResult.Loading

        viewModelScope.launch {
            try {
                val response = RetrofitInstance.getApiService(getApplication()).loginUser(LoginRequest(username, password))

                if (response.isSuccessful && response.body() != null) {
                    val loginResponse = response.body()!!
                    if (loginResponse.success) { // Dodatno preverjanje polja "success" iz vašega API-ja
                        _loginResult.value = LoginResult.Success(loginResponse)
                    } else {
                        // Če API vrne 200 OK, ampak success=false
                        _loginResult.value = LoginResult.Error(loginResponse.message ?: "Neznana napaka s strežnika.")
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    var errorMessage = "Neznana napaka pri prijavi (Koda: ${response.code()})"
                    if (errorBody != null) {
                        try {
                            // Poskusimo razčleniti kot ApiErrorResponse
                            val apiError = Gson().fromJson(errorBody, ApiErrorResponse::class.java)
                            errorMessage = apiError.message ?: apiError.errorDetails ?: "Napaka s strežnika (Koda: ${response.code()})."
                        } catch (e: Exception) {
                            // Ni uspelo razčleniti, morda je samo string
                            errorMessage = "Napaka: $errorBody (Koda: ${response.code()})"
                        }
                    }
                    _loginResult.value = LoginResult.Error(errorMessage)
                }
            } catch (e: Exception) {
                _loginResult.value = LoginResult.Error("Napaka pri povezavi: ${e.localizedMessage ?: e.message}")
            }
        }
    }
}