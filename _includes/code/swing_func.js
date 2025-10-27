if (doc["shoot_command"] == "shoot") {

        // get shoot power

        let shoot_power = parseInt(doc["shoot_power"]);

        // do the shot (via Port B)

        let shoot_code =  "import hub, time\n";

        shoot_code += "from hub import port\n";

        shoot_code += "def swing(degrees, power):\n";

        shoot_code += "    swingSpeed = int(power)\n";

        shoot_code += "    drawSpeed = int(power * 0.25)\n";

        shoot_code += "    time.sleep(0.5)\n";

        shoot_code += "    motor.run_for_degrees(port.B, degrees, drawSpeed)\n"; // Draw

        //shoot_code += "    await motor.run_to_relative_position(port.F, 90, " + shoot_power + ")\n"; // shoot!

        shoot_code += "    time.sleep(1)\n";

        shoot_code += "    motor.run_for_degrees(port.B, -2 * degrees, swingSpeed)\n"; // Swing

        shoot_code += "    time.sleep(3)\n";

        shoot_code += "    motor.run_for_degrees(port.B, degrees, drawSpeed)\n\n"; //Reset

        //shoot_code += "    await motor.run_to_relative_position(port.F, -20, " + shoot_power + ")\n\n"; // reset

        shoot_code += "swing(75, " + shoot_power + ");";

        console.log("Shooting");

        runcode(shoot_code);

        // after running, need to put "pause" in database so new commands register

        db_update("shoot_command", "pause");

    }