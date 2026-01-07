package com.example.pametnipaketnik

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.pametnipaketnik.databinding.ActivityTspBinding
import com.example.pametnipaketnik.tsp.GA
import com.example.pametnipaketnik.tsp.GAWithProgress
import com.example.pametnipaketnik.tsp.RandomUtils
import com.example.pametnipaketnik.tsp.TSP
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.delay
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*

class TSPActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityTspBinding
    private var currentTSP: TSP? = null
    private var bestTour: TSP.Tour? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTspBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
    }
    
    private fun setupUI() {
        val instances = arrayOf("bays29.tsp", "eil101.tsp", "a280.tsp", "pr1002.tsp", "dca1389.tsp")
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, instances)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spinnerInstance.adapter = adapter
        
        binding.buttonStart.setOnClickListener {
            startTSPExecution()
        }
        
        
        binding.buttonRunAllTests.setOnClickListener {
            runAllTests()
        }
        
        binding.buttonBack.setOnClickListener {
            finish()
        }
    }
    
    private fun runAllTests() {
        val instances = arrayOf("bays29.tsp", "eil101.tsp", "a280.tsp", "pr1002.tsp", "dca1389.tsp")

        RandomUtils.setSeed(123)

        binding.buttonStart.isEnabled = false
        binding.buttonRunAllTests.isEnabled = false
        binding.progressBar.visibility = View.VISIBLE
        binding.textResults.text = "ZAGON VSEH TSP TESTOV\n\n" +
            "Opomba: 'Run All' uporablja pospešen način za velike instance,\n" +
            "da se čas izvajanja skrajša. Za polno specifikacijo (30 tekov,\n" +
            "1000*d, pop=100) uporabite gumb Start za posamezno instanco.\n\n"
        
        lifecycleScope.launch {
            try {
                for ((index, instance) in instances.withIndex()) {
                    Log.i("TSP_RUN", "RunAll: starting instance ${index + 1}/5: $instance")
                    runOnUiThread {
                        binding.textResults.append("=== INSTANCA ${index + 1}/5: $instance ===\n")
                    }
                    
                    val results = withContext(Dispatchers.IO) {
                        executeTSPAlgorithmWithTimeout(instance, 100, 0.8, 0.1, 30)
                    }
                    
                    runOnUiThread {
                        if (results.isNotEmpty()) {
                            val best = results.minOrNull() ?: 0.0
                            val average = results.average()
                            binding.textResults.append("Končano: Najbolši=${best.toInt()}, Povprečje=${average.toInt()}\n\n")
                            Log.i("TSP_RUN", "RunAll: finished $instance, runs=${results.size}, best=${best.toInt()}, avg=${average.toInt()}")
                        } else {
                            binding.textResults.append("NAPAKA: Ni rezultatov za $instance\n\n")
                            Log.w("TSP_RUN", "RunAll: no results for $instance")
                        }
                    }
                    
                    saveResultsToFile(results, instance)
                }
                
                runOnUiThread {
                    binding.textResults.append("=== VSI TESTI KONČANI ===\n")
                    binding.textResults.append("Generirane datoteke v /home/matic/Desktop/pametni-paketnik/PJ/rezultati/:\n")
                    instances.forEach { instance ->
                        val instanceName = instance.replace(".tsp", "")
                        binding.textResults.append("• Poštar_$instanceName.txt\n")
                    }
                }
                
            } catch (e: Exception) {
                runOnUiThread {
                    binding.textResults.append("NAPAKA: ${e.message}\n")
                }
            } finally {
                runOnUiThread {
                    binding.buttonStart.isEnabled = true
                    binding.buttonRunAllTests.isEnabled = true
                    binding.progressBar.visibility = View.GONE
                }
                
                RandomUtils.setSeedFromTime()
            }
        }
    }
    
    private fun startTSPExecution() {
        val selectedInstance = binding.spinnerInstance.selectedItem as String
        val popSize = binding.editPopSize.text.toString().toIntOrNull() ?: 100
        val crossoverRate = binding.editCrossover.text.toString().toDoubleOrNull() ?: 0.8
        val mutationRate = binding.editMutation.text.toString().toDoubleOrNull() ?: 0.1
        val maxRuns = 30

        com.example.pametnipaketnik.tsp.RandomUtils.setSeed(123)

        binding.buttonStart.isEnabled = false
        binding.progressBar.visibility = View.VISIBLE
        binding.textResults.text = "Izvajam TSP algoritme...\n"
        
        lifecycleScope.launch {
            try {
                val results = withContext(Dispatchers.IO) {
                    executeTSPAlgorithm(selectedInstance, popSize, crossoverRate, mutationRate, maxRuns)
                }
                
                displayResults(results, selectedInstance)
                saveResultsToFile(results, selectedInstance)
                
            } catch (e: Exception) {
                binding.textResults.text = "Napaka: ${e.message}"
            } finally {
                binding.buttonStart.isEnabled = true
                binding.progressBar.visibility = View.GONE
                
                RandomUtils.setSeedFromTime()
            }
        }
    }
    
    
    private fun executeTSPAlgorithmWithTimeout(
        instance: String, 
        popSize: Int, 
        crossoverRate: Double, 
        mutationRate: Double,
        maxRuns: Int
    ): List<Double> {
        val results = mutableListOf<Double>()
        
        val instanceName = instance.replace(".tsp", "")
        val dimension = when (instanceName) {
            "bays29" -> 29
            "eil101" -> 101
            "a280" -> 280
            "pr1002" -> 1002
            "dca1389" -> 1389
            else -> 100
        }
        val (actualRuns, actualPop, maxFes) = when {
            dimension <= 120 -> Triple(30, 100, 1000 * dimension)
            dimension <= 300 -> Triple(minOf(maxRuns, 15), 90, 800 * dimension)
            dimension <= 1000 -> Triple(minOf(maxRuns, 5), 60, 400 * dimension)
            else -> Triple(minOf(maxRuns, 3), 40, 200 * dimension)
        }
        
        for (run in 1..actualRuns) {
            try {
                runOnUiThread {
                    binding.textResults.append("Run $run/$actualRuns - $instanceName ($dimension mesta)\n")
                }
                Log.i("TSP_RUN", "RunAll: $instanceName run $run/$actualRuns (d=$dimension, pop=$actualPop, maxFes=$maxFes)")
                
                val tsp = TSP(this, instance, maxFes)
                val actualPopSize = actualPop
                
                val ga = GAWithProgress(actualPopSize, crossoverRate, mutationRate) { generation, evaluations, maxEvaluations, bestDistance ->
                    val step = when {
                        dimension <= 120 -> 10
                        dimension <= 300 -> 25
                        else -> 100
                    }
                    if (generation % step == 0 || generation <= 5) {
                        try {
                            runOnUiThread {
                                binding.textResults.append("  Gen $generation: ${bestDistance.toInt()}\n")
                            }
                        } catch (e: Exception) {
                            Log.w("TSP_UI", "UI update failed, continuing execution: ${e.message}")
                        }
                        Log.d("TSP_PROGRESS", "$instanceName gen=$generation best=${bestDistance.toInt()} evals=$evaluations/$maxEvaluations")
                    }
                }
                
                val bestSolution = ga.execute(tsp)
                
                if (bestSolution != null) {
                    results.add(bestSolution.distance)
                    runOnUiThread {
                        binding.textResults.append("  Razdalja: ${bestSolution.distance.toInt()}\n")
                    }
                    Log.i("TSP_RUN", "RunAll: $instanceName run $run best=${bestSolution.distance.toInt()} evals=${tsp.numberOfEvaluations}/${tsp.maxEvaluations}")
                }
                
            } catch (e: Exception) {
                runOnUiThread {
                    binding.textResults.append("  NAPAKA: ${e.message}\n")
                }
                Log.e("TSP_RUN", "RunAll: error on $instanceName run $run: ${e.message}")
            }
        }
        
        return results
    }
    
    private fun executeTSPAlgorithm(
        instance: String, 
        popSize: Int, 
        crossoverRate: Double, 
        mutationRate: Double,
        maxRuns: Int
    ): List<Double> {
        val results = mutableListOf<Double>()
        
        val instanceName = instance.replace(".tsp", "")
        val dimension = when (instanceName) {
            "bays29" -> 29
            "eil101" -> 101
            "a280" -> 280
            "pr1002" -> 1002
            "dca1389" -> 1389
            else -> 100
        }
        
        val maxFes = 1000 * dimension
        
        for (run in 1..maxRuns) {
            val tsp = TSP(this, instance, maxFes)
            currentTSP = tsp
            
            runOnUiThread {
                binding.textResults.append("Run $run/$maxRuns - ${tsp.name} (${tsp.numberOfCities} mesta)\n")
            }
            
            val progressListener = GAWithProgress.ProgressListener { generation, evaluations, maxEvaluations, bestDistance ->
                val step = when {
                    dimension <= 120 -> 10
                    dimension <= 300 -> 25
                    else -> 100
                }
                if (generation % step == 0 || generation < 5) {
                    try {
                        runOnUiThread {
                            binding.textResults.append("  Gen $generation: Najbolja razdalja = ${bestDistance.toInt()}, Eval = $evaluations/$maxEvaluations\n")
                        }
                    } catch (e: Exception) {
                        Log.w("TSP_UI", "UI update failed, continuing execution: ${e.message}")
                    }
                    Log.d("TSP_PROGRESS", "${instanceName} gen=$generation best=${bestDistance.toInt()} evals=$evaluations/$maxEvaluations")
                }
            }
            
            val ga = GAWithProgress(popSize, crossoverRate, mutationRate, progressListener)
            val bestSolution = ga.execute(tsp)
            
            if (bestSolution != null) {
                results.add(bestSolution.distance)
                if (bestTour == null || bestSolution.distance < bestTour!!.distance) {
                    bestTour = bestSolution
                }
                
                runOnUiThread {
                    binding.textResults.append("  Najboljša razdalja: ${bestSolution.distance.toInt()}\n")
                    binding.textResults.append("  Evaluacije: ${tsp.numberOfEvaluations}/${tsp.maxEvaluations}\n\n")
                }
            }
        }
        
        return results
    }
    
    private fun displayResults(results: List<Double>, instanceName: String) {
        if (results.isNotEmpty()) {
            val best = results.minOrNull() ?: 0.0
            val worst = results.maxOrNull() ?: 0.0
            val average = results.average()
            
            val summary = StringBuilder()
            summary.append("\n=== KONČNI REZULTATI ===\n")
            summary.append("Najboljši rezultat: ${best.toInt()}\n")
            summary.append("Najslabši rezultat: ${worst.toInt()}\n")
            summary.append("Povprečje: ${average.toInt()}\n")
            summary.append("Število tekov: ${results.size}\n\n")
            
            summary.append("Vsi rezultati:\n")
            results.forEachIndexed { index, result ->
                summary.append("${index + 1}: ${result.toInt()}\n")
            }
            
            binding.textResults.append(summary.toString())
            
            currentTSP?.let { tsp ->
                val expectedOptimal = getExpectedOptimal(tsp.name ?: "")
                if (expectedOptimal > 0) {
                    val quality = ((best - expectedOptimal) / expectedOptimal * 100)
                    summary.append("\nKvaliteta rešitve:\n")
                    summary.append("Optimalna vrednost: $expectedOptimal\n")
                    summary.append("Odstopanje: ${String.format("%.1f", quality)}%\n")
                    
                    if (quality < 50) {
                        summary.append("Dober rezultat!")
                    } else {
                        summary.append("Rezultat bi lahko bil boljši")
                    }
                    
                    binding.textResults.append(summary.toString())
                }
            }
        }
        
        Toast.makeText(this, "TSP algoritmi končani!", Toast.LENGTH_SHORT).show()
    }
    
    private fun saveResultsToFile(results: List<Double>, instanceName: String) {
        val teamName = "Postar"
        val instanceBaseName = instanceName.replace(".tsp", "")
        val fileName = "${teamName}_${instanceBaseName}.txt"
        
        val saveLocations = listOf(
            File("/home/matic/Desktop/pametni-paketnik/PJ/rezultati"),
            File(android.os.Environment.getExternalStorageDirectory(), "TSP_Results"),
            File(filesDir, "TSP_Results"),
            File(cacheDir, "TSP_Results"),
            File("/tmp/TSP_Results")
        )
        
        var savedSuccessfully = false
        
        for (directory in saveLocations) {
            try {
                if (!directory.exists()) {
                    directory.mkdirs()
                }
                
                val file = File(directory, fileName)
                val writer = FileWriter(file)
                for (result in results) {
                    writer.write("${result.toInt()}\n")
                }
                writer.close()
                
                runOnUiThread {
                    binding.textResults.append("Rezultati shranjeni v: ${file.absolutePath}\n")
                }
                savedSuccessfully = true
                break
                
            } catch (e: Exception) {
                continue
            }
        }
        
        if (!savedSuccessfully) {
            runOnUiThread {
                binding.textResults.append("NAPAKA: Ni bilo mogoče shraniti rezultatov v nobeno lokacijo!\n")
            }
        }
    }
    
    private fun getExpectedOptimal(instanceName: String): Int {
        return when (instanceName) {
            "bays29" -> 2020
            "eil101" -> 629
            "a280" -> 2579
            "pr1002" -> 259045
            "dca1389" -> 80000
            else -> 0
        }
    }
}
