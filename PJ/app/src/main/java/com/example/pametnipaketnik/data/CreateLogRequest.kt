package com.example.pametnipaketnik.data

data class CreateLogRequest(
    val boxId: Int,
    val status: String, // "SUCCESS" ali "FAILURE"
    val message: String,
    val responseCode: Int
)