package com.example.pametnipaketnik.network

import com.example.pametnipaketnik.data.LoginRequest
import com.example.pametnipaketnik.data.LoginResponse
import com.example.pametnipaketnik.data.UserResponse
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Header

data class GetUserProfileResponse(
    val success: Boolean,
    val user: UserResponse
)

interface ApiService {
    @POST("auth/login")
    suspend fun loginUser(@Body loginRequest: LoginRequest): Response<LoginResponse>
    @GET("auth/me")
    suspend fun getCurrentUserProfile(@Header("Authorization") token: String): Response<GetUserProfileResponse>
}