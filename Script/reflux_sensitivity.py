import csv
import os

# ============================================================
# GET DWSIM OBJECTS
# ============================================================

dc = Flowsheet.GetFlowsheetSimulationObject("DC -1")
dist = Flowsheet.GetFlowsheetSimulationObject("Distillate")
bot = Flowsheet.GetFlowsheetSimulationObject("Bottoms")

# Reflux ratios to investigate
reflux_ratios = [1.5, 2.0, 2.5, 3.0, 3.5]

# Store results
results = []

print("========================================")
print("ETHANOL-WATER DISTILLATION SENSITIVITY")
print("========================================")

# ============================================================
# RUN EACH CASE
# ============================================================

for R in reflux_ratios:

    print("")
    print("Running reflux ratio:", R)

    try:

        # Set the actual condenser reflux specification
        dc.SetPropertyValue("Condenser_Specification_Value", R)

        # Solve the flowsheet
        Flowsheet.RequestCalculationAndWait()

        # Read product streams
        dist_flow = dist.GetMolarFlow()
        bot_flow = bot.GetMolarFlow()

        dist_comp = dist.GetOverallComposition()
        bot_comp = bot.GetOverallComposition()

        # Component order is Water, Ethanol
        dist_ethanol = dist_comp[1]
        bot_ethanol = bot_comp[1]

        # Read duties
        condenser_duty = dc.CondenserDuty
        reboiler_duty = dc.ReboilerDuty

        # Ethanol recovery
        feed_ethanol = 100.0 * 0.5
        dist_ethanol_flow = dist_flow * dist_ethanol

        recovery = (dist_ethanol_flow / feed_ethanol) * 100.0

        # Store results
        results.append([
            R,
            dist_flow,
            dist_ethanol * 100.0,
            bot_flow,
            bot_ethanol * 100.0,
            condenser_duty,
            abs(reboiler_duty),
            recovery
        ])

        # Print results
        print("  Distillate flow:", dist_flow)
        print("  Distillate ethanol:", dist_ethanol * 100.0, "%")
        print("  Bottoms flow:", bot_flow)
        print("  Bottoms ethanol:", bot_ethanol * 100.0, "%")
        print("  Condenser duty:", condenser_duty, "kW")
        print("  Reboiler duty:", abs(reboiler_duty), "kW")
        print("  Ethanol recovery:", recovery, "%")
        print("  SUCCESS")

    except Exception as e:

        print("  ERROR:", str(e))


# ============================================================
# WRITE RESULTS TO CSV
# ============================================================

filename = os.path.join(
   os.path.expanduser("~"),
 "Ethanol_Water_Reflux_Sensitivity.csv"
)

with open(filename, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Reflux Ratio",
        "Distillate Flow (mol/s)",
        "Distillate Ethanol (mol%)",
        "Bottoms Flow (mol/s)",
        "Bottoms Ethanol (mol%)",
        "Condenser Duty (kW)",
        "Reboiler Duty (kW)",
        "Ethanol Recovery (%)"
    ])

    for row in results:
        writer.writerow(row)


# ============================================================
# FINISHED
# ============================================================

print("")
print("========================================")
print("SENSITIVITY STUDY COMPLETE")
print("========================================")
print("Number of successful cases:", len(results))
print("Excel-compatible CSV created at:")
print(filename)