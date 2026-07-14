import pcbnew

board = pcbnew.GetBoard()

LEFT_SIDE = ["K19","K34","K33","K32","K31","K30","K29","K28"]
RIGHT_SIDE = ["K27","K26","K20","K21","K25","K24","K23","K22"]
VERTICAL_OFFSET_MM = 25.0
HORIZONTAL_OFFSET_MM = 10.0

for fp in board.GetFootprints():
    ref = fp.GetReference()

    if ref in LEFT_SIDE:
        # Rotate 90 degrees about its own center
        current = fp.GetOrientationDegrees()
        fp.SetOrientationDegrees(current + 90)

        # Move left side: up and left
        pos = fp.GetPosition()
        pos.y -= pcbnew.FromMM(VERTICAL_OFFSET_MM)
        pos.x -= pcbnew.FromMM(HORIZONTAL_OFFSET_MM)
        fp.SetPosition(pos)

    elif ref in RIGHT_SIDE:
        # Rotate 90 degrees about its own center
        current = fp.GetOrientationDegrees()
        fp.SetOrientationDegrees(current + 90)

        # Move right side: down and right
        pos = fp.GetPosition()
        pos.y += pcbnew.FromMM(VERTICAL_OFFSET_MM)
        pos.x += pcbnew.FromMM(HORIZONTAL_OFFSET_MM)
        fp.SetPosition(pos)

pcbnew.Refresh()
