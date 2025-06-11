package com.example.pametnipaketnik.ui.home

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.example.pametnipaketnik.OpenBoxRepository
import com.example.pametnipaketnik.QrScanActivity
import com.example.pametnipaketnik.databinding.FragmentHomeBinding
import kotlinx.coroutines.launch

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val TAG = "HomeFragment"

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.buttonScanQr.setOnClickListener {
            val intent = Intent(requireContext(), QrScanActivity::class.java)
            startActivityForResult(intent, 1001)
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 1001 && resultCode == Activity.RESULT_OK) {
            val boxIdStr = data?.getStringExtra("BOX_ID")
            val boxId = OpenBoxRepository.extractBoxId(boxIdStr)
            if (boxId != null) {
                Toast.makeText(requireContext(), "Predvajam žeton...", Toast.LENGTH_SHORT).show()
                viewLifecycleOwner.lifecycleScope.launch {

                    OpenBoxRepository.openBoxAndLog(requireContext(), boxId, 2) {

                        showConfirmationDialog(boxId, "Predvajanje končano", 200)
                    }
                }
            } else {
                Toast.makeText(requireContext(), "QR koda ne vsebuje veljavnega ID-ja: $boxIdStr", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showConfirmationDialog(boxId: Int, apiMessage: String, responseCode: Int) {
        AlertDialog.Builder(requireContext())
            .setTitle("Potrditev odpiranja")
            .setMessage("Ali se je paketnik uspešno odprl?")
            .setCancelable(false)
            .setPositiveButton("Da") { _, _ ->
                logResult(boxId, "SUCCESS", apiMessage, responseCode)
            }
            .setNegativeButton("Ne") { _, _ ->
                logResult(boxId, "FAILURE", apiMessage, responseCode)
            }
            .show()
    }

    private fun logResult(boxId: Int, status: String, apiMessage: String, responseCode: Int) {
        viewLifecycleOwner.lifecycleScope.launch {
            OpenBoxRepository.logAttempt(requireContext(), boxId, status, apiMessage, responseCode)
            Toast.makeText(requireContext(), "Rezultat zabeležen.", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}