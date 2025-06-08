package com.example.pametnipaketnik.network

import com.example.pametnipaketnik.RegisterRequest
import com.example.pametnipaketnik.RegisterResponse
import com.example.pametnipaketnik.data.CreateLogRequest
import com.example.pametnipaketnik.data.GetLogsResponse
import com.example.pametnipaketnik.data.LoginRequest
import com.example.pametnipaketnik.data.LoginResponse
import com.example.pametnipaketnik.data.UserResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Multipart

data class GetUserProfileResponse(
    val success: Boolean,
    val user: UserResponse
)

data class FaceRegistrationResponse(
    val success: Boolean,
    val message: String,
    val embeddings_count: Int
)

data class FaceVerificationResponse(
    val success: Boolean,
    val verified: Boolean,
    val message: String,
    val similarity_score: Double,
    val threshold: Double
)

interface ApiService {
    @POST("auth/login")
    suspend fun loginUser(@Body loginRequest: LoginRequest): Response<LoginResponse>


    @POST("auth/register")
    suspend fun registerUser(@Body registerRequest: RegisterRequest): Response<RegisterResponse>

    @GET("auth/me")
    suspend fun getCurrentUserProfile(): Response<GetUserProfileResponse>

    @POST("api/logs")
    suspend fun createLog(
        @Body logRequest: CreateLogRequest
    ): Response<Unit>

    @GET("api/logs")
    suspend fun getLogs(): Response<GetLogsResponse>
    suspend fun getCurrentUserProfile(@Header("Authorization") token: String): Response<GetUserProfileResponse>

    @Multipart
    @POST("face/register")
    suspend fun registerFace(
        @Header("Authorization") token: String,
        @Part image: MultipartBody.Part
    ): Response<FaceRegistrationResponse>

    @Multipart
    @POST("face/verify")
    suspend fun verifyFace(
        @Header("Authorization") token: String,
        @Part("user_id") userId: RequestBody,
        @Part image: MultipartBody.Part
    ): Response<FaceVerificationResponse>
}

