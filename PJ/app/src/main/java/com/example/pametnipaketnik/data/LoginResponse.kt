package com.example.pametnipaketnik.data

data class LoginResponse(
    val success: Boolean,
    val message: String?,
    val token: String,
    val user: UserResponse?
)