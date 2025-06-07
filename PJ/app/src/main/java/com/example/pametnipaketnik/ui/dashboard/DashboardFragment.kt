// File: ui/dashboard/DashboardFragment.kt
package com.example.pametnipaketnik.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.example.pametnipaketnik.databinding.FragmentDashboardBinding

class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!

    // Inicializiramo ViewModel
    private val dashboardViewModel: DashboardViewModel by viewModels()

    // Inicializiramo Adapter z praznim seznamom
    private val logsAdapter = LogsAdapter(emptyList())

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Nastavimo RecyclerView
        binding.recyclerViewLogs.adapter = logsAdapter

        // Opazujemo spremembe v ViewModelu
        observeViewModel()

        // Sprožimo pridobivanje podatkov, ko je fragment ustvarjen
        dashboardViewModel.fetchLogs()
    }

    private fun observeViewModel() {
        dashboardViewModel.logs.observe(viewLifecycleOwner) { result ->
            when (result) {
                is LogsResult.Loading -> {
                    binding.progressBar.isVisible = true
                    binding.textError.isVisible = false
                    binding.recyclerViewLogs.isVisible = false
                }
                is LogsResult.Success -> {
                    binding.progressBar.isVisible = false
                    binding.textError.isVisible = false
                    binding.recyclerViewLogs.isVisible = true
                    if (result.logs.isEmpty()) {
                        binding.textError.text = "Zgodovina je prazna."
                        binding.textError.isVisible = true
                        binding.recyclerViewLogs.isVisible = false
                    } else {
                        logsAdapter.updateLogs(result.logs)
                    }
                }
                is LogsResult.Error -> {
                    binding.progressBar.isVisible = false
                    binding.textError.isVisible = true
                    binding.recyclerViewLogs.isVisible = false
                    binding.textError.text = result.message
                    Toast.makeText(requireContext(), result.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}