package com.example.pametnipaketnik

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.pametnipaketnik.network.FaceRegistrationResponse
import com.example.pametnipaketnik.network.RetrofitInstance
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import okhttp3.MultipartBody

sealed class FaceRegistrationResult {
    object Loading : FaceRegistrationResult()
    data class Success(val response: FaceRegistrationResponse) : FaceRegistrationResult()
    data class Error(val message: String) : FaceRegistrationResult()
}

class FaceRegistrationViewModel : ViewModel() {

    private val _registrationResult = MutableLiveData<FaceRegistrationResult>()
    val registrationResult: LiveData<FaceRegistrationResult> = _registrationResult


    fun registerFace(token: String, imagePart: MultipartBody.Part) {
        _registrationResult.value = FaceRegistrationResult.Loading

        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    withTimeout(30000) {
                        val response = RetrofitInstance.api.registerFace(token, imagePart)

                        if (response.isSuccessful && response.body() != null) {
                            _registrationResult.postValue(FaceRegistrationResult.Success(response.body()!!))
                        } else {
                            val errorBody = response.errorBody()?.string()
                            val errorMessage = if (errorBody != null) {
                                try {
                                    Gson().fromJson(errorBody, FaceRegistrationResponse::class.java).message
                                } catch (e: Exception) {
                                    "Error: ${response.code()}"
                                }
                            } else {
                                "Unknown error: ${response.code()}"
                            }
                            _registrationResult.postValue(FaceRegistrationResult.Error(errorMessage))
                        }
                    }
                }
            } catch (e: TimeoutCancellationException) {
                _registrationResult.postValue(FaceRegistrationResult.Error("Request timed out. The server might still be processing your registration."))
            } catch (e: Exception) {
                _registrationResult.postValue(FaceRegistrationResult.Error("Network error: ${e.message}"))
            }
        }
    }


}