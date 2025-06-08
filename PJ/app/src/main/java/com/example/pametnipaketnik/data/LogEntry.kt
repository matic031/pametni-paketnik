package com.example.pametnipaketnik.data

import com.google.gson.annotations.SerializedName

data class LogEntry(
    @SerializedName("_id") val id: String,
    val boxId: Int,
    val status: String,
    val message: String,
    val responseCode: Int,
    val user: String,
    val createdAt: String,
    val updatedAt: String
)