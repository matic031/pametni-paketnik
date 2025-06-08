package com.example.pametnipaketnik

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.pametnipaketnik.network.FaceVerificationResponse
import com.example.pametnipaketnik.network.RetrofitInstance
import com.google.gson.Gson
import kotlinx.coroutines.launch
import okhttp3.MultipartBody
import okhttp3.RequestBody

sealed class FaceVerificationResult {
    object Loading : FaceVerificationResult()
    data class Success(val response: FaceVerificationResponse) : FaceVerificationResult()
    data class Error(val message: String) : FaceVerificationResult()
}

class FaceVerificationViewModel : ViewModel() {

    private val _verificationResult = MutableLiveData<FaceVerificationResult>()
    val verificationResult: LiveData<FaceVerificationResult> = _verificationResult

    fun verifyFace(token: String, userId: RequestBody, imagePart: MultipartBody.Part) {
        _verificationResult.value = FaceVerificationResult.Loading

        viewModelScope.launch {
            try {
                val response = RetrofitInstance.api.verifyFace(token, userId, imagePart)
                if (response.isSuccessful && response.body() != null) {
                    _verificationResult.value = FaceVerificationResult.Success(response.body()!!)
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = if (errorBody != null) {
                        try {
                            Gson().fromJson(errorBody, FaceVerificationResponse::class.java).message
                        } catch (e: Exception) {
                            "Error: ${response.code()}"
                        }
                    } else {
                        "Unknown error: ${response.code()}"
                    }
                    _verificationResult.value = FaceVerificationResult.Error(errorMessage)
                }
            } catch (e: Exception) {
                _verificationResult.value = FaceVerificationResult.Error("Network error: ${e.message}")
            }
        }
    }
}