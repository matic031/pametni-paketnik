package com.example.pametnipaketnik.data

import com.google.gson.annotations.SerializedName

data class LoginResponse(
    @SerializedName("success")
    val success: Boolean,

    @SerializedName("message")
    val message: String?,

    @SerializedName("token")
    val token: String,

    @SerializedName("user")
    val user: UserResponse?
)
