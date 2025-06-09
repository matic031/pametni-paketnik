package com.example.pametnipaketnik.ui.home

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import com.example.pametnipaketnik.LoginActivity
import com.example.pametnipaketnik.OpenBoxRepository
import com.example.pametnipaketnik.QrScanActivity
import com.example.pametnipaketnik.databinding.FragmentHomeBinding
import com.example.pametnipaketnik.network.RetrofitInstance
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
        Log.d(TAG, "onCreateView: Checking authentication")

        val homeViewModel = ViewModelProvider(this).get(HomeViewModel::class.java)
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        val root: View = binding.root

        val textView: TextView = binding.textHome
        homeViewModel.text.observe(viewLifecycleOwner) {
            textView.text = it
        }
        return root
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
                Toast.makeText(requireContext(), "Playing token", Toast.LENGTH_SHORT).show()
                viewLifecycleOwner.lifecycleScope.launch {
                    android.util.Log.d("HomeFragment", "Loaded box with ID: $boxId")
                    OpenBoxRepository.openBoxAndLog(requireContext(), boxId, 2)
                }
            } else {
                Toast.makeText(requireContext(), "QR code does not contain a valid box ID: $boxIdStr", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}