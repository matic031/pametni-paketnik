package com.example.pametnipaketnik.data

data class LoginResponse(
    val success: Boolean,
    val message: String?,
    val token: String? = null,
    val user: UserResponse? = null,
    val faceRegistered: Boolean? = null,
    val lastFaceVerification: String? = null,
    val requiresFaceVerification: Boolean? = null,
    val userId: String? = null
)