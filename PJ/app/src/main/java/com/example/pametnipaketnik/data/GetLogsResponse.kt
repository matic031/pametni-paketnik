package com.example.pametnipaketnik.data

data class GetLogsResponse(
    val success: Boolean,
    val logs: List<LogEntry>
)
