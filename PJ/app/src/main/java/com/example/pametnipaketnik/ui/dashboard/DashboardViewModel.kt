package com.example.pametnipaketnik.ui.dashboard

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.pametnipaketnik.data.LogEntry
import com.example.pametnipaketnik.network.RetrofitInstance
import kotlinx.coroutines.launch

sealed class LogsResult {
    data class Success(val logs: List<LogEntry>) : LogsResult()
    data class Error(val message: String) : LogsResult()
    object Loading : LogsResult()
}

class DashboardViewModel(application: Application) : AndroidViewModel(application) {

    private val _logs = MutableLiveData<LogsResult>()
    val logs: LiveData<LogsResult> = _logs

    fun fetchLogs() {
        _logs.value = LogsResult.Loading
        viewModelScope.launch {
            try {
                val response = RetrofitInstance.getApiService(getApplication()).getLogs()
                if (response.isSuccessful && response.body() != null) {
                    _logs.value = LogsResult.Success(response.body()!!.logs)
                } else {
                    _logs.value = LogsResult.Error("Napaka pri pridobivanju zgodovine (Koda: ${response.code()})")
                }
            } catch (e: Exception) {
                _logs.value = LogsResult.Error("Napaka pri povezavi: ${e.message}")
            }
        }
    }
}