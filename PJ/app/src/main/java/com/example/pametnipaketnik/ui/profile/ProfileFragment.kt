package com.example.pametnipaketnik.ui.profile // Prilagodite paket

import android.content.Context
import android.content.Intent
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.viewModels // Za by viewModels()
import androidx.navigation.fragment.findNavController
import com.example.pametnipaketnik.LoginActivity
import com.example.pametnipaketnik.R
import com.example.pametnipaketnik.databinding.FragmentProfileBinding


class ProfileFragment : Fragment() {

    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!

    private val profileViewModel: ProfileViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        profileViewModel.fetchUserProfile() // začne nalaganje podatkov ob ustvarjanju pogleda

        binding.buttonLogoutProfile.setOnClickListener {
            profileViewModel.performLogout()
        }

        observeViewModel()
    }

    private fun observeViewModel() {
        profileViewModel.userProfileData.observe(viewLifecycleOwner) { result ->
            when (result) {
                is ProfileDataResult.Loading -> {
                    binding.progressBarProfile.visibility = View.VISIBLE
                    binding.textViewProfileError.visibility = View.GONE
                    setProfileDataVisibility(View.GONE)
                }
                is ProfileDataResult.Success -> {
                    binding.progressBarProfile.visibility = View.GONE
                    binding.textViewProfileError.visibility = View.GONE
                    setProfileDataVisibility(View.VISIBLE)
                    result.userProfile.user.let { user ->

                        binding.textViewWelcomeMessage.text = "Dobrodošli, ${user.name ?: user.username}!"
                        binding.textViewUsername.text = user.username
                        binding.textViewEmail.text = user.email
                        binding.textViewName.text = user.name ?: "-"
                        binding.textViewLastName.text = user.lastName ?: "-"
                    }
                }
                is ProfileDataResult.Error -> {
                    binding.progressBarProfile.visibility = View.GONE
                    setProfileDataVisibility(View.GONE) // Skrije podatkovna polja ob napaki
                    binding.textViewProfileError.text = result.message
                    binding.textViewProfileError.visibility = View.VISIBLE
                }
            }
        }

        profileViewModel.logoutComplete.observe(viewLifecycleOwner) { loggedOut ->
            if (loggedOut) {
                navigateToLoginScreen()
                profileViewModel.onLogoutNavigated() // Ponastavi stanje
            }
        }
    }

    private fun setProfileDataVisibility(visibility: Int) {
        binding.textViewWelcomeMessage.visibility = visibility
        // binding.textViewLoginSubtitle.visibility = visibility // Ta je bil odstranjen iz XML-a
        binding.cardMojiPodatki.visibility = visibility
        // Če želite skriti/prikazati tudi gumb za odjavo med nalaganjem, ga dodajte sem:
        // binding.buttonLogoutProfile.visibility = visibility
    }

    private fun navigateToLoginScreen() {
        // Preverimo, ali je aktivnost še vedno prisotna, preden poskusimo klicati kontekst
        if (activity == null || !isAdded) return

        val intent = Intent(activity, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        activity?.finish() // Zapre MainActivity (ali katero koli gostiteljsko aktivnost)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Prepreči memory leak
    }
}