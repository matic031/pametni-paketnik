package com.example.pametnipaketnik.data

data class UserResponse(
    val id: String,
    val username: String,
    val email: String,
    val name: String?,
    val lastName: String?,
    val isAdmin: Boolean,
    val faceRegistered: Boolean,
    val lastFaceVerification: String?
)