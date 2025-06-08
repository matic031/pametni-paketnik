package com.example.pametnipaketnik.ui.profile

import com.example.pametnipaketnik.data.TokenManager
import android.app.Application
import android.content.Context
import android.content.Intent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.pametnipaketnik.data.ApiErrorResponse
import com.example.pametnipaketnik.network.GetUserProfileResponse
import com.example.pametnipaketnik.network.RetrofitInstance
import com.google.gson.Gson
import kotlinx.coroutines.launch

sealed class ProfileDataResult {
    data class Success(val userProfile: GetUserProfileResponse) : ProfileDataResult()
    data class Error(val message: String) : ProfileDataResult()
    object Loading : ProfileDataResult()
}

// ViewModel za ProfileFragment
class ProfileViewModel(application: Application) : AndroidViewModel(application) {

    private val userProfileDataMutable = MutableLiveData<ProfileDataResult>()
    val userProfileData: LiveData<ProfileDataResult> = userProfileDataMutable

    private val logoutCompleteMutable = MutableLiveData<Boolean>()
    val logoutComplete: LiveData<Boolean> = logoutCompleteMutable

    private val _showFaceRegistrationMutable = MutableLiveData<Boolean>()
    val showFaceRegistration: LiveData<Boolean> = _showFaceRegistrationMutable

    // SharedPreferences za dostop do žetona
    private val sharedPreferences = application.getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)

    fun fetchUserProfile() {
        userProfileDataMutable.value = ProfileDataResult.Loading

        viewModelScope.launch {
            try {
                val response = RetrofitInstance.getApiService(getApplication()).getCurrentUserProfile() // Pošljemo žeton v glavi
                if (response.isSuccessful && response.body() != null) {
                    val profileResponse = response.body()!!
                    if (profileResponse.success) {
                        userProfileDataMutable.value = ProfileDataResult.Success(profileResponse)

                        if (!profileResponse.user.faceRegistered) {
                            _showFaceRegistrationMutable.value = true
                        }
                    } else {
                        userProfileDataMutable.value = ProfileDataResult.Error(profileResponse.user.toString() ?: "Napaka pri pridobivanju profila s strežnika.")
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    var errorMessage = "Neznana napaka pri pridobivanju profila (Koda: ${response.code()})"
                    if (errorBody != null) {
                        try {
                            val apiError = Gson().fromJson(errorBody, ApiErrorResponse::class.java)
                            errorMessage = apiError.message ?: apiError.errorDetails ?: "Napaka s strežnika (Koda: ${response.code()})."
                            if (response.code() == 401 || response.code() == 403) { // Neavtoriziran ali prepovedan dostop
                                logoutCompleteMutable.value = true // Sproži odjavo
                            }
                        } catch (e: Exception) {
                            errorMessage = "Napaka: $errorBody (Koda: ${response.code()})"
                        }
                    }
                    userProfileDataMutable.value = ProfileDataResult.Error(errorMessage)
                }
            } catch (e: Exception) {
                userProfileDataMutable.value = ProfileDataResult.Error("Napaka pri povezavi: ${e.localizedMessage}")
            }
        }
    }

    fun performLogout() {
        TokenManager.clearToken(getApplication())
        logoutCompleteMutable.value = true
    }

    fun onLogoutNavigated() {
        logoutCompleteMutable.value = false // Ponastavi stanje po navigaciji
    }

    fun onFaceRegistrationNavigated() {
        _showFaceRegistrationMutable.value = false
    }
}