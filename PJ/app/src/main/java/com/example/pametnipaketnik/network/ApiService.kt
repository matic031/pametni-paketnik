package com.example.pametnipaketnik.network

import com.example.pametnipaketnik.data.LoginRequest
import com.example.pametnipaketnik.data.LoginResponse
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Response

interface ApiService {
    @POST("auth/login")
    suspend fun loginUser(@Body loginRequest: LoginRequest): Response<LoginResponse>
}