package com.example.pametnipaketnik.data

import com.google.gson.annotations.SerializedName

data class ApiErrorResponse(
    @SerializedName("success")
    val success: Boolean?,

    @SerializedName("message")
    val message: String?,

    @SerializedName("error")
    val errorDetails: String?
)
