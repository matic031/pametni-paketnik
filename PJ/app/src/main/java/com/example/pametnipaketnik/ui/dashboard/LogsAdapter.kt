// File: ui/dashboard/LogsAdapter.kt
package com.example.pametnipaketnik.ui.dashboard

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.example.pametnipaketnik.R
import com.example.pametnipaketnik.data.LogEntry
import com.example.pametnipaketnik.databinding.ItemLogBinding

import java.text.SimpleDateFormat
import java.util.*

class LogsAdapter(private var logs: List<LogEntry>) : RecyclerView.Adapter<LogsAdapter.LogViewHolder>() {

    // Definicije za formatiranje datuma
    private val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US).apply {
        timeZone = TimeZone.getTimeZone("UTC")
    }
    private val outputFormat = SimpleDateFormat("dd. MMMM yyyy, HH:mm:ss", Locale("sl"))

    class LogViewHolder(val binding: ItemLogBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LogViewHolder {
        val binding = ItemLogBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return LogViewHolder(binding)
    }

    override fun onBindViewHolder(holder: LogViewHolder, position: Int) {
        val log = logs[position]
        val context = holder.itemView.context // Potrebujemo context za dostop do barv

        with(holder.binding) {
            // Nastavimo ID paketnika in datum
            textLogBoxId.text = "ID paketnika: ${log.boxId}"
            textLogTimestamp.text = formatTimestampCompat(log.createdAt)

            // Logika za status, barvo in ikono
            if (log.status.equals("SUCCESS", ignoreCase = true)) {
                textLogStatus.text = "SUCCESS"
                textLogStatus.setTextColor(ContextCompat.getColor(context, R.color.status_success))
                //iconStatus.setImageResource(R.drawable.ic_success)
            } else {
                textLogStatus.text = "FAILURE"
                textLogStatus.setTextColor(ContextCompat.getColor(context, R.color.status_failure))
                //iconStatus.setImageResource(R.drawable.ic_failure)
            }
        }
    }

    override fun getItemCount() = logs.size

    fun updateLogs(newLogs: List<LogEntry>) {
        this.logs = newLogs
        notifyDataSetChanged()
    }

    private fun formatTimestampCompat(isoTimestamp: String): String {
        return try {
            val date = inputFormat.parse(isoTimestamp)
            if (date != null) {
                outputFormat.format(date)
            } else {
                isoTimestamp
            }
        } catch (e: Exception) {
            e.printStackTrace()
            isoTimestamp
        }
    }
}