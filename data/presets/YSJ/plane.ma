//Maya ASCII 2025ff03 scene
//Name: plane.ma
//Last modified: Fri, Apr 03, 2026 09:02:04 PM
//Codeset: 936
requires maya "2025ff03";
requires "stereoCamera" "10.0";
requires "mtoa" "5.5.4.1";
requires -nodeType "quatToEuler" -nodeType "quatNormalize" "quatNodes" "1.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2025";
fileInfo "version" "2025";
fileInfo "cutIdentifier" "202409190603-cbdc5a7e54";
fileInfo "osv" "Windows 10 Pro v2009 (Build: 19045)";
fileInfo "UUID" "96D3BF30-4F34-FFD7-FDC6-B7AE89D732B3";
createNode transform -n "MFacePlanes";
	rename -uid "A16B303A-4279-3389-E7A8-CDA40DCD27EA";
	setAttr ".t" -type "double3" 0 13.195607681000098 8.3266726846886741e-16 ;
	setAttr ".rp" -type "double3" 0.28340934712248078 154.09999189975809 10.520153907456175 ;
	setAttr ".sp" -type "double3" 0.28340934712248078 154.09999189975809 10.520153907456175 ;
createNode transform -n "L_Mouth_A_ctrl_zero" -p "MFacePlanes";
	rename -uid "FC209DE6-451C-6A5B-A833-70BC4D40E6D9";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "L_Mouth_UD" -ln "L_Mouth_UD" -at "double";
	addAttr -ci true -sn "L_Mouth_LR" -ln "L_Mouth_LR" -at "double";
	addAttr -ci true -sn "L_Mouth_FB" -ln "L_Mouth_FB" -at "double";
	addAttr -ci true -sn "L_Mouth_LUD" -ln "L_Mouth_LUD" -at "double";
	addAttr -ci true -sn "L_Mouth_RUD" -ln "L_Mouth_RUD" -at "double";
	addAttr -ci true -sn "L_Mouth_Twist" -ln "L_Mouth_Twist" -at "double";
	addAttr -ci true -sn "LR_Mouth_LR" -ln "LR_Mouth_LR" -at "double";
	addAttr -ci true -sn "L_Mouth_roundUpper" -ln "L_Mouth_roundUpper" -at "double";
	addAttr -ci true -sn "L_Mouth_roundLower" -ln "L_Mouth_roundLower" -at "double";
	addAttr -ci true -sn "L_Mouth_seal" -ln "L_Mouth_seal" -at "double";
	addAttr -ci true -sn "L_Mouth_OUD" -ln "L_Mouth_OUD" -at "double";
	addAttr -ci true -sn "L_Mouth_OLR" -ln "L_Mouth_OLR" -at "double";
	addAttr -ci true -sn "L_Mouth_OFB" -ln "L_Mouth_OFB" -at "double";
	addAttr -ci true -sn "L_Mouth_OLUD" -ln "L_Mouth_OLUD" -at "double";
	addAttr -ci true -sn "L_Mouth_ORUD" -ln "L_Mouth_ORUD" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "OpenUp" -ln "OpenUp" -at "double";
	addAttr -ci true -sn "OpenDown" -ln "OpenDown" -at "double";
	addAttr -ci true -sn "OpenLeft" -ln "OpenLeft" -at "double";
	addAttr -ci true -sn "OpenRight" -ln "OpenRight" -at "double";
	addAttr -ci true -sn "OpenFront" -ln "OpenFront" -at "double";
	addAttr -ci true -sn "OpenBack" -ln "OpenBack" -at "double";
	addAttr -ci true -sn "OpenLeftUpX" -ln "OpenLeftUpX" -at "double";
	addAttr -ci true -sn "OpenLeftUpY" -ln "OpenLeftUpY" -at "double";
	addAttr -ci true -sn "OpenLeftDownX" -ln "OpenLeftDownX" -at "double";
	addAttr -ci true -sn "OpenLeftDownY" -ln "OpenLeftDownY" -at "double";
	addAttr -ci true -sn "OpenRightUpX" -ln "OpenRightUpX" -at "double";
	addAttr -ci true -sn "OpenRightUpY" -ln "OpenRightUpY" -at "double";
	addAttr -ci true -sn "OpenRightDownX" -ln "OpenRightDownX" -at "double";
	addAttr -ci true -sn "OpenRightDownY" -ln "OpenRightDownY" -at "double";
	addAttr -ci true -sn "LRRight" -ln "LRRight" -at "double";
	addAttr -ci true -sn "LRLeft" -ln "LRLeft" -at "double";
	addAttr -ci true -sn "L_MouthNose_LUD" -ln "L_MouthNose_LUD" -at "double";
	setAttr ".t" -type "double3" 2.9188272302503204 150.02965050057185 10.378935231435911 ;
	setAttr ".r" -type "double3" 0 25.090749150435332 0 ;
	setAttr ".s" -type "double3" 1.0212 1.0212 1.0212 ;
	setAttr -l on -k on "._";
	setAttr -k on ".L_Mouth_UD";
	setAttr -k on ".L_Mouth_LR";
	setAttr -k on ".L_Mouth_FB";
	setAttr -k on ".L_Mouth_LUD";
	setAttr -k on ".L_Mouth_RUD";
	setAttr -k on ".L_Mouth_Twist";
	setAttr -k on ".LR_Mouth_LR";
	setAttr -k on ".L_Mouth_roundUpper";
	setAttr -k on ".L_Mouth_roundLower";
	setAttr -k on ".L_Mouth_seal";
	setAttr -k on ".L_Mouth_OUD";
	setAttr -k on ".L_Mouth_OLR";
	setAttr -k on ".L_Mouth_OFB";
	setAttr -k on ".L_Mouth_OLUD";
	setAttr -k on ".L_Mouth_ORUD";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 10;
	setAttr -k on ".Back" -10;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".OpenUp" 1;
	setAttr -k on ".OpenDown" -1;
	setAttr -k on ".OpenLeft" 1;
	setAttr -k on ".OpenRight" -1;
	setAttr -k on ".OpenFront" 1;
	setAttr -k on ".OpenBack" -1;
	setAttr -k on ".OpenLeftUpX" 1;
	setAttr -k on ".OpenLeftUpY" 1;
	setAttr -k on ".OpenLeftDownX" 1;
	setAttr -k on ".OpenLeftDownY" -1;
	setAttr -k on ".OpenRightUpX" -1;
	setAttr -k on ".OpenRightUpY" 1;
	setAttr -k on ".OpenRightDownX" -1;
	setAttr -k on ".OpenRightDownY" -1;
	setAttr -k on ".LRRight" -1;
	setAttr -k on ".LRLeft" 1;
	setAttr -k on ".L_MouthNose_LUD";
createNode transform -n "L_Mouth_A_ctrl" -p "L_Mouth_A_ctrl_zero";
	rename -uid "0B193DC8-43DC-7638-A9EE-40A58E34B531";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "L_Mouth_A_ctrlShape" -p "L_Mouth_A_ctrl";
	rename -uid "ABC5E635-4040-2061-0D64-82AA5AE38B5D";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 6 0 no 3
		7 0 1 4 6 10 15 16
		7
		2.3048108227627742e-17 0 0
		0.68062762041245728 0.39296053986302654 1.8159387037564514e-15
		2.3048108227627742e-17 0 0
		0.68062762041245739 -0.39296053986302665 1.8159387037564514e-15
		2.3048108227627742e-17 0 0
		0.68062762041245728 0.39296053986302654 1.8159387037564514e-15
		0.68062762041245739 -0.39296053986302665 1.8159387037564514e-15
		;
createNode transform -n "R_Mouth_A_ctrl_zero" -p "MFacePlanes";
	rename -uid "90E1A85D-476F-D47A-B207-4CA16B13A9F9";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "R_Mouth_UD" -ln "R_Mouth_UD" -at "double";
	addAttr -ci true -sn "R_Mouth_LR" -ln "R_Mouth_LR" -at "double";
	addAttr -ci true -sn "R_Mouth_FB" -ln "R_Mouth_FB" -at "double";
	addAttr -ci true -sn "R_Mouth_LUD" -ln "R_Mouth_LUD" -at "double";
	addAttr -ci true -sn "R_Mouth_RUD" -ln "R_Mouth_RUD" -at "double";
	addAttr -ci true -sn "R_Mouth_Twist" -ln "R_Mouth_Twist" -at "double";
	addAttr -ci true -sn "R_Mouth_roundUpper" -ln "R_Mouth_roundUpper" -at "double";
	addAttr -ci true -sn "R_Mouth_roundLower" -ln "R_Mouth_roundLower" -at "double";
	addAttr -ci true -sn "R_Mouth_seal" -ln "R_Mouth_seal" -at "double";
	addAttr -ci true -sn "R_Mouth_OUD" -ln "R_Mouth_OUD" -at "double";
	addAttr -ci true -sn "R_Mouth_OLR" -ln "R_Mouth_OLR" -at "double";
	addAttr -ci true -sn "R_Mouth_OFB" -ln "R_Mouth_OFB" -at "double";
	addAttr -ci true -sn "R_Mouth_OLUD" -ln "R_Mouth_OLUD" -at "double";
	addAttr -ci true -sn "R_Mouth_ORUD" -ln "R_Mouth_ORUD" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "OpenUp" -ln "OpenUp" -at "double";
	addAttr -ci true -sn "OpenDown" -ln "OpenDown" -at "double";
	addAttr -ci true -sn "OpenLeft" -ln "OpenLeft" -at "double";
	addAttr -ci true -sn "OpenRight" -ln "OpenRight" -at "double";
	addAttr -ci true -sn "OpenFront" -ln "OpenFront" -at "double";
	addAttr -ci true -sn "OpenBack" -ln "OpenBack" -at "double";
	addAttr -ci true -sn "OpenLeftUpX" -ln "OpenLeftUpX" -at "double";
	addAttr -ci true -sn "OpenLeftUpY" -ln "OpenLeftUpY" -at "double";
	addAttr -ci true -sn "OpenLeftDownX" -ln "OpenLeftDownX" -at "double";
	addAttr -ci true -sn "OpenLeftDownY" -ln "OpenLeftDownY" -at "double";
	addAttr -ci true -sn "OpenRightUpX" -ln "OpenRightUpX" -at "double";
	addAttr -ci true -sn "OpenRightUpY" -ln "OpenRightUpY" -at "double";
	addAttr -ci true -sn "OpenRightDownX" -ln "OpenRightDownX" -at "double";
	addAttr -ci true -sn "OpenRightDownY" -ln "OpenRightDownY" -at "double";
	addAttr -ci true -sn "R_MouthNose_LUD" -ln "R_MouthNose_LUD" -at "double";
	setAttr ".t" -type "double3" -2.9188273007070387 150.02965050057196 10.378935223230007 ;
	setAttr ".r" -type "double3" 0 154.90924854216422 0 ;
	setAttr ".s" -type "double3" 1.0212 1.0212 -1.0212 ;
	setAttr -l on -k on "._";
	setAttr -k on ".R_Mouth_UD";
	setAttr -k on ".R_Mouth_LR";
	setAttr -k on ".R_Mouth_FB";
	setAttr -k on ".R_Mouth_LUD";
	setAttr -k on ".R_Mouth_RUD";
	setAttr -k on ".R_Mouth_Twist";
	setAttr -k on ".R_Mouth_roundUpper";
	setAttr -k on ".R_Mouth_roundLower";
	setAttr -k on ".R_Mouth_seal";
	setAttr -k on ".R_Mouth_OUD";
	setAttr -k on ".R_Mouth_OLR";
	setAttr -k on ".R_Mouth_OFB";
	setAttr -k on ".R_Mouth_OLUD";
	setAttr -k on ".R_Mouth_ORUD";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 10;
	setAttr -k on ".Back" -10;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".OpenUp" 1;
	setAttr -k on ".OpenDown" -1;
	setAttr -k on ".OpenLeft" 1;
	setAttr -k on ".OpenRight" -1;
	setAttr -k on ".OpenFront" 1;
	setAttr -k on ".OpenBack" -1;
	setAttr -k on ".OpenLeftUpX" 1;
	setAttr -k on ".OpenLeftUpY" 1;
	setAttr -k on ".OpenLeftDownX" 1;
	setAttr -k on ".OpenLeftDownY" -1;
	setAttr -k on ".OpenRightUpX" -1;
	setAttr -k on ".OpenRightUpY" 1;
	setAttr -k on ".OpenRightDownX" -1;
	setAttr -k on ".OpenRightDownY" -1;
	setAttr -k on ".R_MouthNose_LUD";
createNode transform -n "R_Mouth_A_ctrl" -p "R_Mouth_A_ctrl_zero";
	rename -uid "BD4FDC8E-4DEE-EE74-DC2E-B4B7FE979B8F";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr ".s" -type "double3" 1.0000000000000002 1 1 ;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "R_Mouth_A_ctrlShape" -p "R_Mouth_A_ctrl";
	rename -uid "08A03431-4B85-6459-DBC0-E0B341EE1A3E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 6 0 no 3
		7 0 1 4 6 10 15 16
		7
		-1.1102230246251565e-15 0 -3.5527136788005009e-15
		0.68062762041245617 0.39296053986302582 -1.7763568394002505e-15
		-1.1102230246251565e-15 0 -3.5527136788005009e-15
		0.68062762041245617 -0.39296053986299739 -1.7763568394002505e-15
		-1.1102230246251565e-15 0 -3.5527136788005009e-15
		0.68062762041245617 0.39296053986302582 -1.7763568394002505e-15
		0.68062762041245617 -0.39296053986299739 -1.7763568394002505e-15
		;
createNode transform -n "M_LoLip_A_ctrl_zero" -p "MFacePlanes";
	rename -uid "79C0F326-46A0-D1B0-F1F0-83BF801335F1";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "M_LoLip_UD" -ln "M_LoLip_UD" -at "double";
	addAttr -ci true -sn "M_LoLip_LR" -ln "M_LoLip_LR" -at "double";
	addAttr -ci true -sn "M_LoLip_FB" -ln "M_LoLip_FB" -at "double";
	addAttr -ci true -sn "M_LoLip_LUD" -ln "M_LoLip_LUD" -at "double";
	addAttr -ci true -sn "M_LoLip_RUD" -ln "M_LoLip_RUD" -at "double";
	addAttr -ci true -sn "M_LoLip_Twist" -ln "M_LoLip_Twist" -at "double";
	addAttr -ci true -sn "M_LoLip_Roll" -ln "M_LoLip_Roll" -at "double";
	addAttr -ci true -sn "M_LoLip_Spin" -ln "M_LoLip_Spin" -at "double";
	addAttr -ci true -sn "M_LoLip_funnel" -ln "M_LoLip_funnel" -at "double";
	addAttr -ci true -sn "M_LoLip_press" -ln "M_LoLip_press" -at "double";
	addAttr -ci true -sn "M_LoLip_puff" -ln "M_LoLip_puff" -at "double";
	addAttr -ci true -sn "M_LoLip_thicknessY" -ln "M_LoLip_thicknessY" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "TwistPos" -ln "TwistPos" -at "double";
	addAttr -ci true -sn "TwistNeg" -ln "TwistNeg" -at "double";
	addAttr -ci true -sn "RollPos" -ln "RollPos" -at "double";
	addAttr -ci true -sn "RollNeg" -ln "RollNeg" -at "double";
	addAttr -ci true -sn "SpinPos" -ln "SpinPos" -at "double";
	addAttr -ci true -sn "SpinNeg" -ln "SpinNeg" -at "double";
	addAttr -ci true -sn "funnel" -ln "funnel" -at "double";
	addAttr -ci true -sn "press" -ln "press" -at "double";
	addAttr -ci true -sn "puff" -ln "puff" -at "double";
	addAttr -ci true -sn "thicknessY" -ln "thicknessY" -at "double";
	setAttr ".t" -type "double3" 2.6367796834847152e-16 149.17359887278431 12.290174629453496 ;
	setAttr ".s" -type "double3" 1.15995 1.15995 1.15995 ;
	setAttr -l on -k on "._";
	setAttr -k on ".M_LoLip_UD";
	setAttr -k on ".M_LoLip_LR";
	setAttr -k on ".M_LoLip_FB";
	setAttr -k on ".M_LoLip_LUD";
	setAttr -k on ".M_LoLip_RUD";
	setAttr -k on ".M_LoLip_Twist";
	setAttr -k on ".M_LoLip_Roll";
	setAttr -k on ".M_LoLip_Spin";
	setAttr -k on ".M_LoLip_funnel";
	setAttr -k on ".M_LoLip_press";
	setAttr -k on ".M_LoLip_puff";
	setAttr -k on ".M_LoLip_thicknessY";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".TwistPos" 30;
	setAttr -k on ".TwistNeg" -30;
	setAttr -k on ".RollPos" 40;
	setAttr -k on ".RollNeg" -40;
	setAttr -k on ".SpinPos" 30;
	setAttr -k on ".SpinNeg" -30;
	setAttr -k on ".funnel" 10;
	setAttr -k on ".press" 10;
	setAttr -k on ".puff" 10;
	setAttr -k on ".thicknessY" 10;
createNode transform -n "M_LoLip_A_ctrl_sdk" -p "M_LoLip_A_ctrl_zero";
	rename -uid "AD415098-46CA-6C90-6BAF-A6B1E78FBFB1";
	setAttr ".rp" -type "double3" 0 -0.017960315337408245 -8.7292107942012471e-17 ;
	setAttr ".sp" -type "double3" 0 -0.017960315337408245 -8.7292107942012471e-17 ;
createNode transform -n "M_LoLip_A_ctrl" -p "M_LoLip_A_ctrl_sdk";
	rename -uid "C38B86D4-4214-7895-6E8E-2786746F90F8";
	addAttr -ci true -sn "roll" -ln "roll" -min -40 -max 40 -at "double";
	addAttr -ci true -sn "funnel" -ln "funnel" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "press" -ln "press" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "puff" -ln "puff" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "thicknessY" -ln "thicknessY" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "tighten" -ln "tighten" -min 0 -max 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr -k on ".roll";
	setAttr -l on ".funnel";
	setAttr -l on ".press";
	setAttr -k on ".puff";
	setAttr -k on ".thicknessY";
	setAttr -l on ".tighten";
createNode nurbsCurve -n "M_LoLip_A_ctrlShape" -p "M_LoLip_A_ctrl";
	rename -uid "1C6D5E22-447D-3870-3005-84878479838F";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 12;
	setAttr ".ls" 3;
	setAttr ".cc" -type "nurbsCurve" 
		3 20 2 no 3
		25 -0.125 -0.0625 0 0.0625 0.125 0.1875 0.2266615619 0.25 0.3122235471 0.3125
		 0.375 0.43660826619999998 0.43749999999999994 0.5 0.53021912800000004 0.5625 0.625
		 0.6875 0.75 0.8125 0.87499999999999989 0.9375 1 1.0625 1.125
		23
		-0.4025062592460224 0.17464682187984495 -3.2050836795313568e-15
		-0.7962684858904826 0.17464682187984232 -3.7272978946845259e-15
		-0.82784380210268826 0.17127542774553234 0
		-0.82916004938914978 0.13886399223243767 -3.4719084609964827e-15
		-0.80920717183030644 0.046956304153573783 -3.5934112803032735e-15
		-0.73235863517869215 -0.070147415623204409 -3.5608775954454895e-15
		-0.61755417640031718 -0.17511806461687035 -3.5068707585461408e-15
		-0.49709116302523765 -0.2057903842794761 -3.5087738212312854e-15
		-0.40656263249852598 -0.2105674525546046 -3.3296051080626765e-15
		0 -0.20949065604599079 -2.9789509722211355e-15
		0.40656263249852598 -0.2105674525546046 -3.3296051080626765e-15
		0.49709116302523765 -0.2057903842794761 -3.5087738212312854e-15
		0.61755417640031718 -0.17511806461687035 -3.5068707585461408e-15
		0.73235863517869215 -0.070147415623204409 -3.5608775954454895e-15
		0.80920717183030644 0.046956304153573783 -3.5934112803032735e-15
		0.82916004938914978 0.13886399223243767 -3.4719084609964827e-15
		0.82916004938914978 0.17083999772703085 -3.3156253747097645e-15
		0.7962684858904826 0.17464682187984232 -3.7272978946845259e-15
		0.40250625924599803 0.17464682187984495 -3.4109199395187375e-15
		-1.3102654739743572e-14 0.17464682187984495 -3.3842374613722251e-15
		-0.4025062592460224 0.17464682187984495 -3.2050836795313568e-15
		-0.7962684858904826 0.17464682187984232 -3.7272978946845259e-15
		-0.82784380210268826 0.17127542774553234 0
		;
createNode transform -n "M_Mouth_A_ctrl_zero" -p "MFacePlanes";
	rename -uid "D1A6B7C2-48A2-9CEB-F707-41AC0092B874";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "M_Mouth_UD" -ln "M_Mouth_UD" -at "double";
	addAttr -ci true -sn "M_Mouth_LR" -ln "M_Mouth_LR" -at "double";
	addAttr -ci true -sn "M_Mouth_FB" -ln "M_Mouth_FB" -at "double";
	addAttr -ci true -sn "M_Mouth_LUD" -ln "M_Mouth_LUD" -at "double";
	addAttr -ci true -sn "M_Mouth_RUD" -ln "M_Mouth_RUD" -at "double";
	addAttr -ci true -sn "M_Mouth_RotX" -ln "M_Mouth_RotX" -at "double";
	addAttr -ci true -sn "M_Mouth_RotY" -ln "M_Mouth_RotY" -at "double";
	addAttr -ci true -sn "M_Mouth_RotZ" -ln "M_Mouth_RotZ" -at "double";
	addAttr -ci true -sn "M_Mouth_ScaX" -ln "M_Mouth_ScaX" -at "double";
	addAttr -ci true -sn "M_Mouth_ScaY" -ln "M_Mouth_ScaY" -at "double";
	addAttr -ci true -sn "M_Mouth_ScaZ" -ln "M_Mouth_ScaZ" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "RotXPos" -ln "RotXPos" -at "double";
	addAttr -ci true -sn "RotXNeg" -ln "RotXNeg" -at "double";
	addAttr -ci true -sn "RotYPos" -ln "RotYPos" -at "double";
	addAttr -ci true -sn "RotYNeg" -ln "RotYNeg" -at "double";
	addAttr -ci true -sn "RotZPos" -ln "RotZPos" -at "double";
	addAttr -ci true -sn "RotZNeg" -ln "RotZNeg" -at "double";
	setAttr ".t" -type "double3" 2.6367796834847152e-16 149.8695688727843 12.290174629453496 ;
	setAttr ".s" -type "double3" 1.15995 1.15995 1.15995 ;
	setAttr -l on -k on "._";
	setAttr -av -k on ".M_Mouth_UD";
	setAttr -av -k on ".M_Mouth_LR";
	setAttr -k on ".M_Mouth_FB";
	setAttr -k on ".M_Mouth_LUD";
	setAttr -k on ".M_Mouth_RUD";
	setAttr -k on ".M_Mouth_RotX";
	setAttr -k on ".M_Mouth_RotY";
	setAttr -k on ".M_Mouth_RotZ";
	setAttr -k on ".M_Mouth_ScaX" 1;
	setAttr -k on ".M_Mouth_ScaY" 1;
	setAttr -k on ".M_Mouth_ScaZ" 1;
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".RotXPos" 20;
	setAttr -k on ".RotXNeg" 20;
	setAttr -k on ".RotYPos" 20;
	setAttr -k on ".RotYNeg" 20;
	setAttr -k on ".RotZPos" 20;
	setAttr -k on ".RotZNeg" 20;
createNode transform -n "M_Mouth_A_ctrl" -p "M_Mouth_A_ctrl_zero";
	rename -uid "FE5A9B37-41F5-CFC8-40C8-02BF0122E707";
	addAttr -ci true -sn "mouthSec" -ln "mouthSec" -min 0 -max 1 -at "bool";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr -l on ".mouthSec" yes;
createNode nurbsCurve -n "M_Mouth_A_ctrlShape" -p "M_Mouth_A_ctrl";
	rename -uid "7BB30B90-4B2A-97D8-C3DC-1EA8CB3453F0";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".ls" 3;
	setAttr ".cc" -type "nurbsCurve" 
		3 52 0 no 3
		57 0 0 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
		 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52
		 52 52
		55
		0 0.20589331978957137 2.4494872749865953e-16
		0 0.20589331978957137 2.4494872749865953e-16
		0 0.20589331978957137 2.4494872749865953e-16
		0.019413186566684483 0.2295328657659241 2.5706774372941553e-16
		0.057584861906212426 0.26787582210537175 2.4476788236430791e-16
		0.095756537245740278 0.30621877844481926 2.5706774372941553e-16
		0.12603034490747198 0.33560676934646949 2.6918675996017153e-16
		0.20990130476958216 0.36444338902294837 2.4494872749865953e-16
		0.29520926050710916 0.33578660205011107 2.9342479242168353e-16
		0.32514700103765193 0.30810395711680266 2.4494872749865953e-16
		0.47970683485283516 0.15423455422846077 3.0750333909892502e-16
		0.63426666866801829 0.00036515134011871344 2.4494872749865953e-16
		0.6620830691019568 -0.029448352403596469 2.9342479242168353e-16
		0.69112149736122586 -0.11462715514203448 2.4494872749865953e-16
		0.66266066166297344 -0.19862637760221363 2.6918675996017153e-16
		0.63340850281890704 -0.229031453535954 2.5706774372941553e-16
		0.59523682747937934 -0.26737440987540151 2.4494872749865953e-16
		0.55706515213985131 -0.30571736621484918 2.5706774372941553e-16
		0.52679134447811948 -0.33510535711649947 2.6918675996017153e-16
		0.44292038461600935 -0.36394197679297824 2.4494872749865953e-16
		0.35761242887848238 -0.33528518982014099 2.9342479242168353e-16
		0.32767468834793961 -0.30760254488683259 2.4494872749865953e-16
		0.22014561769721308 -0.2003201217886337 2.6918675996017153e-16
		0.22014561769721308 -0.2003201217886337 2.6918675996017153e-16
		0.22014561769721308 -0.2003201217886337 2.6918675996017153e-16
		0.1908254693621548 -0.23065963960261981 2.5706774372941553e-16
		0.15256805766798046 -0.26891705129679411 2.4494872749865953e-16
		0.11431064597380597 -0.30717446299096862 2.5706774372941553e-16
		0.083971128159819872 -0.33649461132602693 2.6918675996017153e-16
		3.5826697150175864e-05 -0.36514341079351509 2.4494872749865953e-16
		-0.085207766120306686 -0.33629573089904063 2.9342479242168353e-16
		-0.11508346311157364 -0.30854613868827596 2.4494872749865953e-16
		-0.22151508598579356 -0.20161090659479253 2.4494872749865953e-16
		-0.22151508598579356 -0.20161090659479253 2.4494872749865953e-16
		-0.22151508598579356 -0.20161090659479253 2.4494872749865953e-16
		-0.32767468834793961 -0.30760254488683259 2.4494872749865953e-16
		-0.35761242887848238 -0.33528518982014099 2.9342479242168353e-16
		-0.44292038461600935 -0.36394197679297824 2.4494872749865953e-16
		-0.52679134447811948 -0.33510535711649947 2.6918675996017153e-16
		-0.55706515213985131 -0.30571736621484918 2.5706774372941553e-16
		-0.59523682747937934 -0.26737440987540151 2.4494872749865953e-16
		-0.63340850281890704 -0.229031453535954 2.5706774372941553e-16
		-0.66266066166297344 -0.19862637760221363 2.6918675996017153e-16
		-0.69112149736122586 -0.11462715514203448 2.4494872749865953e-16
		-0.6620830691019568 -0.029448352403596469 2.9342479242168353e-16
		-0.63426666866801829 0.00036515134011871344 2.4494872749865953e-16
		-0.47970683485283516 0.15423455422846077 3.0750333909892502e-16
		-0.32514700103765193 0.30810395711680266 2.4494872749865953e-16
		-0.29520926050710916 0.33578660205011107 2.9342479242168353e-16
		-0.20990130476958216 0.36444338902294837 2.4494872749865953e-16
		-0.12603034490747198 0.33560676934646949 2.6918675996017153e-16
		-0.095756537245740278 0.30621877844481926 2.5706774372941553e-16
		-0.057584861906212426 0.26787582210537175 2.4476788236430791e-16
		-0.019413186566684483 0.2295328657659241 2.5706774372941553e-16
		0 0.20589331978957137 2.4494872749865953e-16
		;
createNode transform -n "M_UpLip_A_ctrl_zero" -p "MFacePlanes";
	rename -uid "5DE90E30-492A-68DB-4CD8-3590EA6F9C76";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "M_UpLip_UD" -ln "M_UpLip_UD" -at "double";
	addAttr -ci true -sn "M_UpLip_LR" -ln "M_UpLip_LR" -at "double";
	addAttr -ci true -sn "M_UpLip_FB" -ln "M_UpLip_FB" -at "double";
	addAttr -ci true -sn "M_UpLip_LUD" -ln "M_UpLip_LUD" -at "double";
	addAttr -ci true -sn "M_UpLip_RUD" -ln "M_UpLip_RUD" -at "double";
	addAttr -ci true -sn "M_UpLip_Twist" -ln "M_UpLip_Twist" -at "double";
	addAttr -ci true -sn "M_UpLip_Roll" -ln "M_UpLip_Roll" -at "double";
	addAttr -ci true -sn "M_UpLip_Spin" -ln "M_UpLip_Spin" -at "double";
	addAttr -ci true -sn "M_UpLip_funnel" -ln "M_UpLip_funnel" -at "double";
	addAttr -ci true -sn "M_UpLip_press" -ln "M_UpLip_press" -at "double";
	addAttr -ci true -sn "M_UpLip_puff" -ln "M_UpLip_puff" -at "double";
	addAttr -ci true -sn "M_UpLip_thicknessY" -ln "M_UpLip_thicknessY" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "TwistPos" -ln "TwistPos" -at "double";
	addAttr -ci true -sn "TwistNeg" -ln "TwistNeg" -at "double";
	addAttr -ci true -sn "RollPos" -ln "RollPos" -at "double";
	addAttr -ci true -sn "RollNeg" -ln "RollNeg" -at "double";
	addAttr -ci true -sn "SpinPos" -ln "SpinPos" -at "double";
	addAttr -ci true -sn "SpinNeg" -ln "SpinNeg" -at "double";
	addAttr -ci true -sn "funnel" -ln "funnel" -at "double";
	addAttr -ci true -sn "press" -ln "press" -at "double";
	addAttr -ci true -sn "puff" -ln "puff" -at "double";
	addAttr -ci true -sn "thicknessY" -ln "thicknessY" -at "double";
	setAttr ".t" -type "double3" 2.6367796834847152e-16 150.56553887278429 12.290174629453496 ;
	setAttr ".s" -type "double3" 1.15995 1.15995 1.15995 ;
	setAttr -l on -k on "._";
	setAttr -k on ".M_UpLip_UD";
	setAttr -k on ".M_UpLip_LR";
	setAttr -k on ".M_UpLip_FB";
	setAttr -k on ".M_UpLip_LUD";
	setAttr -k on ".M_UpLip_RUD";
	setAttr -k on ".M_UpLip_Twist";
	setAttr -k on ".M_UpLip_Roll";
	setAttr -k on ".M_UpLip_Spin";
	setAttr -k on ".M_UpLip_funnel";
	setAttr -k on ".M_UpLip_press";
	setAttr -k on ".M_UpLip_puff";
	setAttr -k on ".M_UpLip_thicknessY";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".TwistPos" 30;
	setAttr -k on ".TwistNeg" -30;
	setAttr -k on ".RollPos" 40;
	setAttr -k on ".RollNeg" -40;
	setAttr -k on ".SpinPos" 30;
	setAttr -k on ".SpinNeg" -30;
	setAttr -k on ".funnel" 10;
	setAttr -k on ".press" 10;
	setAttr -k on ".puff" 10;
	setAttr -k on ".thicknessY" 10;
createNode transform -n "M_UpLip_A_ctrl_sdk" -p "M_UpLip_A_ctrl_zero";
	rename -uid "F1A7447F-4B0B-BE8E-A2C4-C2AA8C298794";
	setAttr ".rp" -type "double3" 0 0.017960315337379823 -8.7292107942012471e-17 ;
	setAttr ".sp" -type "double3" 0 0.017960315337379823 -8.7292107942012471e-17 ;
createNode transform -n "M_UpLip_A_ctrl" -p "M_UpLip_A_ctrl_sdk";
	rename -uid "B7C74A51-433D-96D3-CE15-DC9E3A195B7F";
	addAttr -ci true -sn "roll" -ln "roll" -min -40 -max 40 -at "double";
	addAttr -ci true -sn "funnel" -ln "funnel" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "press" -ln "press" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "puff" -ln "puff" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "thicknessY" -ln "thicknessY" -min -10 -max 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr -k on ".roll";
	setAttr -l on ".funnel";
	setAttr -l on ".press";
	setAttr -k on ".puff";
	setAttr -k on ".thicknessY";
createNode nurbsCurve -n "M_UpLip_A_ctrlShape" -p "M_UpLip_A_ctrl";
	rename -uid "06CE07A5-4E56-055E-752E-20A20A0519E8";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 12;
	setAttr ".ls" 3;
	setAttr ".cc" -type "nurbsCurve" 
		3 20 2 no 3
		25 -0.125 -0.0625 0 0.0625 0.125 0.1875 0.2266615619 0.25 0.3122235471 0.3125
		 0.375 0.43660826619999998 0.43749999999999994 0.5 0.53021912800000004 0.5625 0.625
		 0.6875 0.75 0.8125 0.87499999999999989 0.9375 1 1.0625 1.125
		23
		-0.4025062592460224 -0.17464682187984495 -3.2050836795313568e-15
		-0.7962684858904826 -0.17464682187984232 -3.7272978946845259e-15
		-0.82784380210268826 -0.17127542774553234 0
		-0.82916004938914978 -0.13886399223243767 -3.4719084609964827e-15
		-0.80920717183030644 -0.046956304153573783 -3.5934112803032735e-15
		-0.73235863517869215 0.070147415623204409 -3.5608775954454895e-15
		-0.61755417640031718 0.17511806461687035 -3.5068707585461408e-15
		-0.49709116302523765 0.2057903842794761 -3.5087738212312854e-15
		-0.40656263249852598 0.2105674525546046 -3.3296051080626765e-15
		0 0.20949065604599079 -2.9789509722211355e-15
		0.40656263249852598 0.2105674525546046 -3.3296051080626765e-15
		0.49709116302523765 0.2057903842794761 -3.5087738212312854e-15
		0.61755417640031718 0.17511806461687035 -3.5068707585461408e-15
		0.73235863517869215 0.070147415623204409 -3.5608775954454895e-15
		0.80920717183030644 -0.046956304153573783 -3.5934112803032735e-15
		0.82916004938914978 -0.13886399223243767 -3.4719084609964827e-15
		0.82916004938914978 -0.17083999772703085 -3.3156253747097645e-15
		0.7962684858904826 -0.17464682187984232 -3.7272978946845259e-15
		0.40250625924599803 -0.17464682187984495 -3.4109199395187375e-15
		-1.3102654739743572e-14 -0.17464682187984495 -3.3842374613722251e-15
		-0.4025062592460224 -0.17464682187984495 -3.2050836795313568e-15
		-0.7962684858904826 -0.17464682187984232 -3.7272978946845259e-15
		-0.82784380210268826 -0.17127542774553234 0
		;
createNode transform -n "L_EyelidCtrl_A_grp" -p "MFacePlanes";
	rename -uid "BEE5EFCC-4E3B-7A40-9B89-079604CBD2D2";
	setAttr ".t" -type "double3" 19.225513462396808 157.2514418334793 12.43076658240159 ;
	setAttr ".s" -type "double3" 1.6239300000000003 1.6239300000000003 1.6239300000000003 ;
createNode transform -n "L_UpLid_A_ctrl_zero" -p "L_EyelidCtrl_A_grp";
	rename -uid "0D59D4B7-43A4-CDDD-FA36-7F9CFDA6D6FD";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "L_UpLid_UD" -ln "L_UpLid_UD" -at "double";
	addAttr -ci true -sn "L_UpLid_LR" -ln "L_UpLid_LR" -at "double";
	addAttr -ci true -sn "L_UpLid_FB" -ln "L_UpLid_FB" -at "double";
	addAttr -ci true -sn "L_UpLid_Twist" -ln "L_UpLid_Twist" -at "double";
	addAttr -ci true -sn "L_UpLid_squint" -ln "L_UpLid_squint" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "TwistPos" -ln "TwistPos" -at "double";
	addAttr -ci true -sn "TwistNeg" -ln "TwistNeg" -at "double";
	addAttr -ci true -sn "Middle" -ln "Middle" -at "double";
	setAttr ".t" -type "double3" 0 1 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr -l on -k on "._";
	setAttr -k on ".L_UpLid_UD";
	setAttr -k on ".L_UpLid_LR";
	setAttr -k on ".L_UpLid_FB";
	setAttr -k on ".L_UpLid_Twist";
	setAttr -k on ".L_UpLid_squint";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".TwistPos" 30;
	setAttr -k on ".TwistNeg" -30;
	setAttr -k on ".Middle" -0.5;
createNode transform -n "L_UpLid_A_ctrl" -p "L_UpLid_A_ctrl_zero";
	rename -uid "1E834663-4A40-6606-1BE9-859BBCE9BC4A";
	addAttr -ci true -sn "followBrow" -ln "followBrow" -min 0 -max 1 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" -1.7763568394002505e-15 0.0015737772591490895 0.0024765799800476884 ;
	setAttr ".sp" -type "double3" -1.7763568394002505e-15 0.0015737772591490895 0.0024765799800476884 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr -l on ".followBrow";
createNode nurbsCurve -n "L_UpLid_A_ctrlShape" -p "L_UpLid_A_ctrl";
	rename -uid "8DD529A2-46AB-BC97-C28F-67A92381ABEA";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		-3.5388206032797488e-15 -0.14753922054964463 0.0011467552628737015
		-0.22184684397328625 -0.14753922054964463 0.0011467552628737015
		-0.54252950693569291 -0.14753922054964361 0.0011467552628737015
		-0.58346711221315783 -0.14753922054964572 0.0011467552628737015
		-0.46064286892660461 0.067722854129154783 0.0011467552628737015
		0.00032916598453803744 0.2209438720278743 0.0011467552628737015
		0.45994633601138402 0.067722854129154783 0.0011467552628737015
		0.58346711221315573 -0.14753922054964572 0.0011467552628737015
		0.54639530816892312 -0.14753922054964361 0.0011467552628737015
		0.22582275236263089 -0.14753922054964463 0.0011467552628737015
		-3.5388206032797488e-15 -0.14753922054964463 0.0011467552628737015
		;
createNode transform -n "L_LoLid_A_ctrl_zero" -p "L_EyelidCtrl_A_grp";
	rename -uid "F425B161-4931-DD1A-6543-DC8E0B3BD5D9";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "L_LoLid_UD" -ln "L_LoLid_UD" -at "double";
	addAttr -ci true -sn "L_LoLid_LR" -ln "L_LoLid_LR" -at "double";
	addAttr -ci true -sn "L_LoLid_FB" -ln "L_LoLid_FB" -at "double";
	addAttr -ci true -sn "L_LoLid_Twist" -ln "L_LoLid_Twist" -at "double";
	addAttr -ci true -sn "L_LoLid_squint" -ln "L_LoLid_squint" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "TwistPos" -ln "TwistPos" -at "double";
	addAttr -ci true -sn "TwistNeg" -ln "TwistNeg" -at "double";
	addAttr -ci true -sn "Middle" -ln "Middle" -at "double";
	setAttr ".t" -type "double3" 0 -1 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr -l on -k on "._";
	setAttr -k on ".L_LoLid_UD";
	setAttr -k on ".L_LoLid_LR";
	setAttr -k on ".L_LoLid_FB";
	setAttr -k on ".L_LoLid_Twist";
	setAttr -k on ".L_LoLid_squint";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".TwistPos" 30;
	setAttr -k on ".TwistNeg" -30;
	setAttr -k on ".Middle" 0.5;
createNode transform -n "L_LoLid_A_ctrl" -p "L_LoLid_A_ctrl_zero";
	rename -uid "EACE17B0-40FA-93E8-C764-77928B506D79";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" -0.00080000150735526354 0.0017697082882364157 0.0025773063482734671 ;
	setAttr ".sp" -type "double3" -0.00080000150735526354 0.0017697082882364157 0.0025773063482734671 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
createNode nurbsCurve -n "L_LoLid_A_ctrlShape" -p "L_LoLid_A_ctrl";
	rename -uid "CDACFB73-4D62-283B-9F88-249A7774009B";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		0.0016037157121051673 0.1330786587141789 0.0026752776991796341
		-0.30827092167708658 0.1330786587141789 0.0026752776991796341
		-0.54408792193196887 0.1330786587141789 0.0026752776991796341
		-0.58335183048791905 0.13307865871417771 0.0026752776991796341
		-0.44504543621577747 -0.088924696489021918 0.0026752776991796341
		0.001811163415629812 -0.21679449639074372 0.0026752776991796341
		0.4451744961494693 -0.088924696489021918 0.0026752776991796341
		0.58289044267674617 0.13307865871417771 0.0026752776991796341
		0.54481043294053644 0.13307865871418015 0.0026752776991796341
		0.31786689168125093 0.1330786587141789 0.0026752776991796341
		0.0016037157121051673 0.1330786587141789 0.0026752776991796341
		;
createNode transform -n "L_EyeCornerInn_A_ctrl_zero" -p "L_EyelidCtrl_A_grp";
	rename -uid "6CB6D74A-4E59-744D-CFD5-FABA0A0B8E63";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "L_EyeCornerInn_UD" -ln "L_EyeCornerInn_UD" -at "double";
	addAttr -ci true -sn "L_EyeCornerInn_LR" -ln "L_EyeCornerInn_LR" -at "double";
	addAttr -ci true -sn "L_EyeCornerInn_FB" -ln "L_EyeCornerInn_FB" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	setAttr ".t" -type "double3" -1.3 0 0 ;
	setAttr -l on -k on "._";
	setAttr -k on ".L_EyeCornerInn_UD";
	setAttr -k on ".L_EyeCornerInn_LR";
	setAttr -k on ".L_EyeCornerInn_FB";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
createNode transform -n "L_EyeCornerInn_A_ctrl" -p "L_EyeCornerInn_A_ctrl_zero";
	rename -uid "203113A9-41FA-9D49-D7F6-89979BF38347";
	addAttr -ci true -sn "followBrow" -ln "followBrow" -min 0 -max 1 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 0 0.0024765799800476884 ;
	setAttr ".sp" -type "double3" 0 0 0.0024765799800476884 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr -l on ".followBrow";
createNode nurbsCurve -n "L_EyeCornerInn_A_ctrlShape" -p "L_EyeCornerInn_A_ctrl";
	rename -uid "5A4B731E-43A0-4146-2459-FEA9371C0271";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		0.17554171399394511 0.00088068553230022059 0.0014210762131978427
		0.17554171399394522 -0.12148454753218829 0.0014210762131978427
		0.17554171399394497 -0.17812441194814926 0.0014210762131978427
		0.17554171399394697 -0.26366049119710711 0.0014210762131978427
		-0.054109290431838465 -0.18208614015231328 0.0014210762131978427
		-0.17554171399394786 0.0010114298884549115 0.0014210762131978427
		-0.054109290431838486 0.18357084913208085 0.0014210762131978427
		0.17554171399394711 0.26542186226171116 0.0014210762131978427
		0.17554171399394511 0.18116128622087138 0.0014210762131978427
		0.17554171399394503 0.12543893134374878 0.0014210762131978427
		0.17554171399394511 0.00088068553230022059 0.0014210762131978427
		;
createNode transform -n "L_EyeCornerOut_A_ctrl_zero" -p "L_EyelidCtrl_A_grp";
	rename -uid "ADE7219D-43DD-39C2-9AC8-0B818EED238A";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "L_EyeCornerOut_UD" -ln "L_EyeCornerOut_UD" -at "double";
	addAttr -ci true -sn "L_EyeCornerOut_LR" -ln "L_EyeCornerOut_LR" -at "double";
	addAttr -ci true -sn "L_EyeCornerOut_FB" -ln "L_EyeCornerOut_FB" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	setAttr ".t" -type "double3" 1.3 0 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr -l on -k on "._";
	setAttr -k on ".L_EyeCornerOut_UD";
	setAttr -k on ".L_EyeCornerOut_LR";
	setAttr -k on ".L_EyeCornerOut_FB";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
createNode transform -n "L_EyeCornerOut_A_ctrl" -p "L_EyeCornerOut_A_ctrl_zero";
	rename -uid "85C108B1-4C49-221C-75B2-76BCAB388FDC";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 0 0.0025773063482734671 ;
	setAttr ".sp" -type "double3" 0 0 0.0025773063482734671 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
createNode nurbsCurve -n "L_EyeCornerOut_A_ctrlShape" -p "L_EyeCornerOut_A_ctrl";
	rename -uid "CF80002C-4374-9C7A-C627-C9AD09E299DC";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		-0.17281084634992275 0.0020335935323281037 0.0026549516918650015
		-0.17281084634992275 -0.1210482613879212 0.0026549516918650015
		-0.17281084634992178 -0.17817649272179806 0.0026549516918650015
		-0.17281084634992025 -0.26304735194696521 0.0026549516918650015
		0.070007596881421982 -0.17537494361359557 0.0026549516918650015
		0.17134839147614211 0.0021159915251547602 0.0026549516918650015
		0.07000759688142201 0.17821940500964314 0.0026549516918650015
		-0.17281084634992019 0.26572127414459495 0.0026549516918650015
		-0.17281084634992278 0.18110047501621737 0.0026549516918650015
		-0.17281084634992275 0.12765296873908855 0.0026549516918650015
		-0.17281084634992275 0.0020335935323281037 0.0026549516918650015
		;
createNode transform -n "L_Eyeball_A_a_ctrl_zero" -p "L_EyelidCtrl_A_grp";
	rename -uid "54B11EA7-4521-8C3E-E777-219AE6E4F911";
	setAttr ".t" -type "double3" 1.5228504679498656e-07 -1.4210854715202004e-14 -2.9357784914196827e-07 ;
	setAttr ".ro" 2;
	setAttr ".s" -type "double3" 0.61579008947429992 0.61579008947429992 0.61579008947429992 ;
createNode transform -n "L_Eyeball_A_a_ctrl" -p "L_Eyeball_A_a_ctrl_zero";
	rename -uid "862FB440-4103-CF1F-5D20-3A8FD9EBFE79";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Scale" -at "enum";
	addAttr -ci true -sn "irisScale" -ln "irisScale" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "pupilScale" -ln "pupilScale" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "EyeBall" -at "enum";
	addAttr -ci true -sn "blink" -ln "blink" -min 0 -max 1 -at "double";
	addAttr -ci true -sn "blinkHeight" -ln "blinkHeight" -dv 0.75 -min 0 -max 1 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 6.9855232709414847e-17 -2.5147883775389345e-15 0 ;
	setAttr ".sp" -type "double3" 6.9855232709414847e-17 -2.5147883775389345e-15 0 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnsl" -type "double3" 0.5 0.5 -1 ;
	setAttr ".mxsl" -type "double3" 2 2 1 ;
	setAttr -l on -k on "._";
	setAttr -k on ".irisScale";
	setAttr -k on ".pupilScale";
	setAttr -l on -k on ".__";
	setAttr -k on ".blink";
	setAttr -k on ".blinkHeight";
createNode nurbsCurve -n "L_Eyeball_A_a_ctrlShape" -p "L_Eyeball_A_a_ctrl";
	rename -uid "16CE9537-4BDB-A511-3388-9DA5B2FE6101";
	setAttr -k off ".v" no;
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 8 0 no 3
		9 0 1 2 3 4 5 6 7 8
		9
		9.5186190282891211e-16 2.2374491365495148e-14 -1.7871575816824432e-07
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		3.317465061087073e-08 0.25298252704612628 3.1202311787941965e-05
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		-0.25298252704612223 2.2116439442122739e-08 3.1202311787941965e-05
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		-1.1058217469473227e-08 -0.25298252704611812 3.1202311787941965e-05
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		0.25298252704612223 4.4945668921440637e-15 3.1202311787941965e-05
		;
createNode nurbsCurve -n "nurbsCircleShape1" -p "L_Eyeball_A_a_ctrl";
	rename -uid "C53F01D1-4EB0-E6FB-E754-EC833751C365";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.24008139906639414 0.24008139906639736 -3.8608033560472571e-17
		6.247235307812678e-16 0.33952637063320412 6.2439592456869493e-33
		-0.24008139906639445 0.24008139906639744 3.8608033560472522e-17
		-0.33952637063320323 7.7132814705616693e-15 5.4600004677775805e-17
		-0.2400813990663945 -0.24008139906639087 3.8608033560472534e-17
		5.5377875869745193e-16 -0.33952637063320179 1.6466798555931632e-32
		0.24008139906639381 -0.24008139906639089 -3.8608033560472479e-17
		0.33952637063320273 7.4325349466384073e-15 -5.4600004677775805e-17
		0.24008139906639414 0.24008139906639736 -3.8608033560472571e-17
		6.247235307812678e-16 0.33952637063320412 6.2439592456869493e-33
		-0.24008139906639445 0.24008139906639744 3.8608033560472522e-17
		;
createNode nurbsCurve -n "nurbsCircleShape3" -p "L_Eyeball_A_a_ctrl";
	rename -uid "77EEE055-430A-9234-C8BC-8B9C4C60D06F";
	setAttr -k off ".v";
	setAttr ".ovdt" 1;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.11747569718810427 0.11747569718810594 -1.8891532943474488e-17
		7.8898086781235891e-17 0.16613572421265352 3.0552698728581317e-33
		-0.11747569718810448 0.11747569718810598 1.8891532943474458e-17
		-0.16613572421265216 1.9599192858346044e-15 2.6716662102679697e-17
		-0.11747569718810463 -0.11747569718810295 1.8891532943474467e-17
		4.4183666610383632e-17 -0.16613572421265069 8.0574698762029657e-33
		0.11747569718810406 -0.117475697188103 -1.8891532943474455e-17
		0.16613572421265185 1.8225454877841272e-15 -2.6716662102679697e-17
		0.11747569718810427 0.11747569718810594 -1.8891532943474488e-17
		7.8898086781235891e-17 0.16613572421265352 3.0552698728581317e-33
		-0.11747569718810448 0.11747569718810598 1.8891532943474458e-17
		;
createNode transform -n "R_EyelidCtrl_A_grp" -p "MFacePlanes";
	rename -uid "5B54F315-4A59-5A85-E614-F7B210F60571";
	setAttr ".t" -type "double3" 10.880548734768725 157.2514418334799 12.430766582401638 ;
	setAttr ".r" -type "double3" 0 180 0 ;
	setAttr ".s" -type "double3" 1.6239300000000003 1.6239300000000003 -1.6239300000000003 ;
createNode transform -n "R_UpLid_A_ctrl_zero" -p "R_EyelidCtrl_A_grp";
	rename -uid "40A58AF0-4788-6428-4D37-08BFE10A69C5";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "R_UpLid_UD" -ln "R_UpLid_UD" -at "double";
	addAttr -ci true -sn "R_UpLid_LR" -ln "R_UpLid_LR" -at "double";
	addAttr -ci true -sn "R_UpLid_FB" -ln "R_UpLid_FB" -at "double";
	addAttr -ci true -sn "R_UpLid_Twist" -ln "R_UpLid_Twist" -at "double";
	addAttr -ci true -sn "R_UpLid_squint" -ln "R_UpLid_squint" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "TwistPos" -ln "TwistPos" -at "double";
	addAttr -ci true -sn "TwistNeg" -ln "TwistNeg" -at "double";
	addAttr -ci true -sn "Middle" -ln "Middle" -at "double";
	setAttr ".t" -type "double3" 0 1 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr -l on -k on "._";
	setAttr -k on ".R_UpLid_UD";
	setAttr -k on ".R_UpLid_LR";
	setAttr -k on ".R_UpLid_FB";
	setAttr -k on ".R_UpLid_Twist";
	setAttr -k on ".R_UpLid_squint";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".TwistPos" 30;
	setAttr -k on ".TwistNeg" -30;
	setAttr -k on ".Middle" -0.5;
createNode transform -n "R_UpLid_A_ctrl" -p "R_UpLid_A_ctrl_zero";
	rename -uid "6AA778DC-4B3F-A750-C294-7BAD35780E34";
	addAttr -ci true -sn "followBrow" -ln "followBrow" -min 0 -max 1 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" -1.7763568394002505e-15 0.0015737772591490895 0.0024765799800476884 ;
	setAttr ".sp" -type "double3" -1.7763568394002505e-15 0.0015737772591490895 0.0024765799800476884 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr -l on ".followBrow";
createNode nurbsCurve -n "R_UpLid_A_ctrlShape" -p "R_UpLid_A_ctrl";
	rename -uid "B24101B0-42DA-87DC-B2DC-5DB9E974DD02";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		-3.5527136788005009e-15 -0.1475392205496604 0.0011467552628738886
		-0.22184684397328613 -0.1475392205496604 0.0011467552628738886
		-0.54252950693569257 -0.1475392205496604 0.0011467552628738886
		-0.5834671122131585 -0.1475392205496604 0.0011467552628738886
		-0.46064286892660444 0.067722854129129928 0.0011467552628738886
		0.00032916598453791579 0.22094387202785981 0.0011467552628738886
		0.45994633601138357 0.067722854129129928 0.0011467552628738886
		0.58346711221315584 -0.1475392205496604 0.0011467552628738886
		0.54639530816892368 -0.1475392205496604 0.0011467552628738886
		0.22582275236263172 -0.1475392205496604 0.0011467552628738886
		-3.5527136788005009e-15 -0.1475392205496604 0.0011467552628738886
		;
createNode transform -n "R_LoLid_A_ctrl_zero" -p "R_EyelidCtrl_A_grp";
	rename -uid "A82A4C93-4365-6EC4-4E95-8BA149945497";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "R_LoLid_UD" -ln "R_LoLid_UD" -at "double";
	addAttr -ci true -sn "R_LoLid_LR" -ln "R_LoLid_LR" -at "double";
	addAttr -ci true -sn "R_LoLid_FB" -ln "R_LoLid_FB" -at "double";
	addAttr -ci true -sn "R_LoLid_Twist" -ln "R_LoLid_Twist" -at "double";
	addAttr -ci true -sn "R_LoLid_squint" -ln "R_LoLid_squint" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	addAttr -ci true -sn "TwistPos" -ln "TwistPos" -at "double";
	addAttr -ci true -sn "TwistNeg" -ln "TwistNeg" -at "double";
	addAttr -ci true -sn "Middle" -ln "Middle" -at "double";
	setAttr ".t" -type "double3" 0 -1 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr -l on -k on "._";
	setAttr -k on ".R_LoLid_UD";
	setAttr -k on ".R_LoLid_LR";
	setAttr -k on ".R_LoLid_FB";
	setAttr -k on ".R_LoLid_Twist";
	setAttr -k on ".R_LoLid_squint";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
	setAttr -k on ".TwistPos" 30;
	setAttr -k on ".TwistNeg" -30;
	setAttr -k on ".Middle" 0.5;
createNode transform -n "R_LoLid_A_ctrl" -p "R_LoLid_A_ctrl_zero";
	rename -uid "640682D6-4B0D-238E-28A2-3C962EB01F83";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" -0.00080000150735526354 0.0017697082882364157 0.0025773063482734671 ;
	setAttr ".sp" -type "double3" -0.00080000150735526354 0.0017697082882364157 0.0025773063482734671 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
createNode nurbsCurve -n "R_LoLid_A_ctrlShape" -p "R_LoLid_A_ctrl";
	rename -uid "C47E9A81-4827-97C6-AD44-058C0A9A53EC";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		0.0016037157121058243 0.13307865871418301 0.0026752776991783023
		-0.30827092167708603 0.13307865871418301 0.0026752776991783023
		-0.54408792193196831 0.13307865871418301 0.0026752776991783023
		-0.58335183048791883 0.13307865871418301 0.0026752776991783023
		-0.44504543621577675 -0.088924696489016242 0.0026752776991783023
		0.001811163415630368 -0.21679449639073312 0.0026752776991783023
		0.44517449614946969 -0.088924696489016242 0.0026752776991783023
		0.58289044267674672 0.13307865871418301 0.0026752776991783023
		0.54481043294053766 0.13307865871418301 0.0026752776991783023
		0.31786689168125282 0.13307865871418301 0.0026752776991783023
		0.0016037157121058243 0.13307865871418301 0.0026752776991783023
		;
createNode transform -n "R_EyeCornerInn_A_ctrl_zero" -p "R_EyelidCtrl_A_grp";
	rename -uid "44CBED32-4379-A246-AB66-22BFA458AB8D";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "R_EyeCornerInn_UD" -ln "R_EyeCornerInn_UD" -at "double";
	addAttr -ci true -sn "R_EyeCornerInn_LR" -ln "R_EyeCornerInn_LR" -at "double";
	addAttr -ci true -sn "R_EyeCornerInn_FB" -ln "R_EyeCornerInn_FB" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	setAttr ".t" -type "double3" -1.3 0 0 ;
	setAttr -l on -k on "._";
	setAttr -k on ".R_EyeCornerInn_UD";
	setAttr -k on ".R_EyeCornerInn_LR";
	setAttr -k on ".R_EyeCornerInn_FB";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
createNode transform -n "R_EyeCornerInn_A_ctrl" -p "R_EyeCornerInn_A_ctrl_zero";
	rename -uid "BC1CEB6B-4DFC-9C32-295F-40904894A96F";
	addAttr -ci true -sn "followBrow" -ln "followBrow" -min 0 -max 1 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 0 0.0024765799800476884 ;
	setAttr ".sp" -type "double3" 0 0 0.0024765799800476884 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr -l on ".followBrow";
createNode nurbsCurve -n "R_EyeCornerInn_A_ctrlShape" -p "R_EyeCornerInn_A_ctrl";
	rename -uid "DF0C1F1D-49A4-2282-E60C-BEA37259CD43";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		0.17554171399394569 0.00088068553230868929 0.0014210762131980914
		0.17554171399394569 -0.12148454753217663 0.0014210762131980914
		0.17554171399394569 -0.1781244119481471 0.0014210762131980914
		0.17554171399394747 -0.26366049119710055 0.0014210762131980914
		-0.054109290431838097 -0.18208614015230751 0.0014210762131980914
		-0.17554171399394747 0.0010114298884786876 0.0014210762131980914
		-0.054109290431838097 0.18357084913209576 0.0014210762131980914
		0.17554171399394747 0.26542186226171793 0.0014210762131980914
		0.17554171399394569 0.18116128622088468 0.0014210762131980914
		0.17554171399394569 0.1254389313437656 0.0014210762131980914
		0.17554171399394569 0.00088068553230868929 0.0014210762131980914
		;
createNode transform -n "R_EyeCornerOut_A_ctrl_zero" -p "R_EyelidCtrl_A_grp";
	rename -uid "82653255-418F-60E0-9EA3-F184404947CA";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "R_EyeCornerOut_UD" -ln "R_EyeCornerOut_UD" -at "double";
	addAttr -ci true -sn "R_EyeCornerOut_LR" -ln "R_EyeCornerOut_LR" -at "double";
	addAttr -ci true -sn "R_EyeCornerOut_FB" -ln "R_EyeCornerOut_FB" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	addAttr -ci true -sn "Up" -ln "Up" -at "double";
	addAttr -ci true -sn "Down" -ln "Down" -at "double";
	addAttr -ci true -sn "Left" -ln "Left" -at "double";
	addAttr -ci true -sn "Right" -ln "Right" -at "double";
	addAttr -ci true -sn "Front" -ln "Front" -at "double";
	addAttr -ci true -sn "Back" -ln "Back" -at "double";
	addAttr -ci true -sn "LeftUpX" -ln "LeftUpX" -at "double";
	addAttr -ci true -sn "LeftUpY" -ln "LeftUpY" -at "double";
	addAttr -ci true -sn "LeftDownX" -ln "LeftDownX" -at "double";
	addAttr -ci true -sn "LeftDownY" -ln "LeftDownY" -at "double";
	addAttr -ci true -sn "RightUpX" -ln "RightUpX" -at "double";
	addAttr -ci true -sn "RightUpY" -ln "RightUpY" -at "double";
	addAttr -ci true -sn "RightDownX" -ln "RightDownX" -at "double";
	addAttr -ci true -sn "RightDownY" -ln "RightDownY" -at "double";
	setAttr ".t" -type "double3" 1.3 0 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr -l on -k on "._";
	setAttr -k on ".R_EyeCornerOut_UD";
	setAttr -k on ".R_EyeCornerOut_LR";
	setAttr -k on ".R_EyeCornerOut_FB";
	setAttr -l on -k on ".__";
	setAttr -k on ".Up" 1;
	setAttr -k on ".Down" -1;
	setAttr -k on ".Left" 1;
	setAttr -k on ".Right" -1;
	setAttr -k on ".Front" 1;
	setAttr -k on ".Back" -1;
	setAttr -k on ".LeftUpX" 1;
	setAttr -k on ".LeftUpY" 1;
	setAttr -k on ".LeftDownX" 1;
	setAttr -k on ".LeftDownY" -1;
	setAttr -k on ".RightUpX" -1;
	setAttr -k on ".RightUpY" 1;
	setAttr -k on ".RightDownX" -1;
	setAttr -k on ".RightDownY" -1;
createNode transform -n "R_EyeCornerOut_A_ctrl" -p "R_EyeCornerOut_A_ctrl_zero";
	rename -uid "C46233ED-470A-82DB-47A0-7B92238E1C59";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 0 0.0025773063482734671 ;
	setAttr ".sp" -type "double3" 0 0 0.0025773063482734671 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
createNode nurbsCurve -n "R_EyeCornerOut_A_ctrlShape" -p "R_EyeCornerOut_A_ctrl";
	rename -uid "B845221A-43B7-57C2-F6EC-4AAB5DD46B3F";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 0 no 3
		13 4 4 4 5 6 7 8 9 10 11 12 12 12
		11
		-0.17281084634992183 0.0020335935323458898 0.0026549516918654703
		-0.17281084634992183 -0.12104826138789804 0.0026549516918654703
		-0.17281084634992183 -0.17817649272177505 0.0026549516918654703
		-0.17281084634991917 -0.26304735194695184 0.0026549516918654703
		0.070007596881422884 -0.17537494361359052 0.0026549516918654703
		0.17134839147614311 0.0021159915251729444 0.0026549516918654703
		0.070007596881422884 0.1782194050096706 0.0026549516918654703
		-0.17281084634991917 0.26572127414461022 0.0026549516918654703
		-0.17281084634992272 0.18110047501622262 0.0026549516918654703
		-0.17281084634992183 0.12765296873909904 0.0026549516918654703
		-0.17281084634992183 0.0020335935323458898 0.0026549516918654703
		;
createNode transform -n "R_Eyeball_A_a_ctrl_zero" -p "R_EyelidCtrl_A_grp";
	rename -uid "6C44D135-4004-A7E6-3B88-76B7D35BFC6B";
	setAttr ".t" -type "double3" 1.5228504679498656e-07 -1.4210854715202004e-14 -2.9357784736561143e-07 ;
	setAttr ".ro" 2;
	setAttr ".s" -type "double3" 0.61579008947429992 0.61579008947429992 0.61579008947429992 ;
createNode transform -n "R_Eyeball_A_a_ctrl" -p "R_Eyeball_A_a_ctrl_zero";
	rename -uid "F9937B28-4342-43C9-6D4A-F7B87959DB56";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Scale" -at "enum";
	addAttr -ci true -sn "irisScale" -ln "irisScale" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "pupilScale" -ln "pupilScale" -min -10 -max 10 -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "EyeBall" -at "enum";
	addAttr -ci true -sn "blink" -ln "blink" -min 0 -max 1 -at "double";
	addAttr -ci true -sn "blinkHeight" -ln "blinkHeight" -dv 0.75 -min 0 -max 1 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 6.9855232709414847e-17 -2.5147883775389345e-15 0 ;
	setAttr ".sp" -type "double3" 6.9855232709414847e-17 -2.5147883775389345e-15 0 ;
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnsl" -type "double3" 0.5 0.5 -1 ;
	setAttr ".mxsl" -type "double3" 2 2 1 ;
	setAttr -l on -k on "._";
	setAttr -k on ".irisScale";
	setAttr -k on ".pupilScale";
	setAttr -l on -k on ".__";
	setAttr -k on ".blink";
	setAttr -k on ".blinkHeight";
createNode nurbsCurve -n "R_Eyeball_A_a_ctrlShape" -p "R_Eyeball_A_a_ctrl";
	rename -uid "4C0C921D-48D1-6DF9-1E2D-AA9FE5554A76";
	setAttr -k off ".v" no;
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 8 0 no 3
		9 0 1 2 3 4 5 6 7 8
		9
		9.5186190282891211e-16 2.2374491365495148e-14 -1.7871575816824432e-07
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		3.317465061087073e-08 0.25298252704612628 3.1202311787941965e-05
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		-0.25298252704612223 2.2116439442122739e-08 3.1202311787941965e-05
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		-1.1058217469473227e-08 -0.25298252704611812 3.1202311787941965e-05
		9.5186190282891211e-16 2.2374491365495148e-14 0.00012302140787892707
		0.25298252704612223 4.4945668921440637e-15 3.1202311787941965e-05
		;
createNode nurbsCurve -n "nurbsCircleShape2" -p "R_Eyeball_A_a_ctrl";
	rename -uid "28DA6178-42E8-8ADF-1FAE-8A9635E583C4";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.24008139906639414 0.24008139906639736 -3.8608033560472571e-17
		6.247235307812678e-16 0.33952637063320412 6.2439592456869493e-33
		-0.24008139906639445 0.24008139906639744 3.8608033560472522e-17
		-0.33952637063320323 7.7132814705616693e-15 5.4600004677775805e-17
		-0.2400813990663945 -0.24008139906639087 3.8608033560472534e-17
		5.5377875869745193e-16 -0.33952637063320179 1.6466798555931632e-32
		0.24008139906639381 -0.24008139906639089 -3.8608033560472479e-17
		0.33952637063320273 7.4325349466384073e-15 -5.4600004677775805e-17
		0.24008139906639414 0.24008139906639736 -3.8608033560472571e-17
		6.247235307812678e-16 0.33952637063320412 6.2439592456869493e-33
		-0.24008139906639445 0.24008139906639744 3.8608033560472522e-17
		;
createNode nurbsCurve -n "nurbsCircleShape4" -p "R_Eyeball_A_a_ctrl";
	rename -uid "AF53DD8C-4F90-99D2-9F0B-08B7B38B5286";
	setAttr -k off ".v";
	setAttr ".ovdt" 1;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.11747569718810427 0.11747569718810594 -1.8891532943474488e-17
		7.8898086781235891e-17 0.16613572421265352 3.0552698728581317e-33
		-0.11747569718810448 0.11747569718810598 1.8891532943474458e-17
		-0.16613572421265216 1.9599192858346044e-15 2.6716662102679697e-17
		-0.11747569718810463 -0.11747569718810295 1.8891532943474467e-17
		4.4183666610383632e-17 -0.16613572421265069 8.0574698762029657e-33
		0.11747569718810406 -0.117475697188103 -1.8891532943474455e-17
		0.16613572421265185 1.8225454877841272e-15 -2.6716662102679697e-17
		0.11747569718810427 0.11747569718810594 -1.8891532943474488e-17
		7.8898086781235891e-17 0.16613572421265352 3.0552698728581317e-33
		-0.11747569718810448 0.11747569718810598 1.8891532943474458e-17
		;
createNode transform -n "M_Phoneme_A_ctrl_zero" -p "MFacePlanes";
	rename -uid "09FFE8DB-4023-F5E0-470B-8A8114E56DB0";
	setAttr -l on -k off ".v";
	setAttr -l on ".lodv";
	setAttr ".t" -type "double3" 15.3104313069607 150.92109648802708 12.275693510834193 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1.16 1.16 1.16 ;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "M_Phoneme_A_Square" -p "M_Phoneme_A_ctrl_zero";
	rename -uid "D814C516-44FA-F798-0DD6-CE84E63F5D53";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".rp" -type "double3" 0.019283908683831119 0.64925371394640252 -0.0003094524798382131 ;
	setAttr ".sp" -type "double3" 0.019283908683831119 0.64925371394640252 -0.0003094524798382131 ;
createNode transform -n "M_Phoneme_A_frame" -p "M_Phoneme_A_Square";
	rename -uid "6B4BFB8F-4262-43D7-1C34-719C73043B9D";
createNode nurbsCurve -n "M_Phoneme_A_frameShape" -p "M_Phoneme_A_frame";
	rename -uid "DEAB27E5-4E35-8F60-C729-C8BE9D9D0E6D";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.82713504633274249 0.82713504633274249 0
		-0.82713504633274249 -0.82713504633274249 0
		0.82713504633274249 -0.82713504633274249 0
		0.82713504633274249 0.82713504633274249 0
		-0.82713504633274249 0.82713504633274249 0
		;
createNode transform -n "M_Phoneme_A_ctrl" -p "M_Phoneme_A_ctrl_zero";
	rename -uid "942FD015-48A3-4AE2-3162-24928AF835EB";
	addAttr -ci true -sn "AA" -ln "AA" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "EE" -ln "EE" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "FF" -ln "FF" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "MM" -ln "MM" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "OO" -ln "OO" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "SS" -ln "SS" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "SH" -ln "SH" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "UU" -ln "UU" -min 0 -max 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ovc" 17;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 0 2.9442166460922771e-17 ;
	setAttr ".sp" -type "double3" 0 0 2.9442166460922771e-17 ;
	setAttr -k on ".AA";
	setAttr -k on ".EE";
	setAttr -k on ".FF";
	setAttr -k on ".MM";
	setAttr -k on ".OO";
	setAttr -k on ".SS";
	setAttr -k on ".SH";
	setAttr -k on ".UU";
createNode nurbsCurve -n "M_Phoneme_A_ctrlShape" -p "M_Phoneme_A_ctrl";
	rename -uid "B270105B-43BE-4490-47E6-8F9CADBBF5F8";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		2 31 0 no 3
		34 0 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
		 27 28 29 30 31 31
		33
		-0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		-0.6057520854289784 -0.06226862835853364 -0.00027861605349244201
		-0.39691441993167054 -0.25670093807619132 -0.00027861605349244201
		-0.16208720694301704 -0.35010465298021032 -0.00027861605349244201
		-1.2224475309352556e-05 -0.36038876512635021 -0.00027861605349244201
		0.1620627579924161 -0.35010465298021032 -0.00027861605349244201
		0.39688997098106782 -0.25670093807619132 -0.00027861605349244201
		0.60547347737691481 -0.062442134260670912 -0.00027861605349244201
		0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		0.28870056585653359 0.024813609841110917 -0.00027861605349244201
		-1.9345623414324109e-05 -0.077161957921152435 -0.00027861605349244201
		-0.28879109465755448 0.024813609841110917 -0.00027861605349244201
		-0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		-0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		-0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		-0.28879109465755448 0.057797007950353141 -0.00027861605349244201
		-1.9345623414324109e-05 -0.00878154293406741 -0.00027861605349244201
		0.28870056585653359 0.057797007950353141 -0.00027861605349244201
		0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		0.62762842360843862 0.068648120071116203 -0.00027861605349244201
		0.34487057836781077 0.36038876512635021 -0.00027861605349244201
		0.1072252786495973 0.29954807978871045 -0.00027861605349244201
		-1.7763568394002505e-14 0.26788717064130552 -0.00027861605349244201
		-0.1072252786496577 0.29954807978871045 -0.00027861605349244201
		-0.34488524199066006 0.36038876512635021 -0.00027861605349244201
		-0.62748745253528604 0.068669502650620551 -0.00027861605349244201
		-0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		-0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		-0.73280020233589838 -0.0026640831271915744 -0.00027861605349244201
		;
createNode transform -n "M_Expression_A_ctrl_zero" -p "MFacePlanes";
	rename -uid "5BD105D1-4816-772B-FCFF-BBA68B37ACC3";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 15.310431306960739 152.1199541479333 12.275693510834223 ;
	setAttr ".s" -type "double3" 1.16 1.16 1.16 ;
createNode transform -n "M_Expression_A_Square" -p "M_Expression_A_ctrl_zero";
	rename -uid "ADFB9BE0-4A2E-16B7-1E50-FD85D4F4218E";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" -0.0019085478798099853 -0.25881864937349297 0 ;
	setAttr ".rp" -type "double3" 0.0019085478798099853 0.25881864937349297 -3.0626823844681183e-05 ;
	setAttr ".sp" -type "double3" 0.0019085478798099853 0.25881864937349297 -3.0626823844681183e-05 ;
createNode transform -n "M_Expression_A_frame" -p "M_Expression_A_Square";
	rename -uid "568E0E3B-4BF8-EDBA-DCFB-A18C914DCF5E";
	setAttr ".rp" -type "double3" 0.0019085478798099853 0.25881864937349297 0 ;
	setAttr ".sp" -type "double3" 0.0019085478798099853 0.25881864937349297 0 ;
createNode nurbsCurve -n "M_Expression_A_frameShape" -p "M_Expression_A_frame";
	rename -uid "F5369278-4FED-33C8-8098-159A5D113516";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.82562126607418318 1.0863484633274862 0
		-0.82562126607418318 -0.56871116458050019 0
		0.82943836183380315 -0.56871116458050019 0
		0.82943836183380315 1.0863484633274862 0
		-0.82562126607418318 1.0863484633274862 0
		;
createNode transform -n "M_Expression_A_ctrl" -p "M_Expression_A_ctrl_zero";
	rename -uid "79A54AC2-4644-5A70-9DD4-5492CA74B3D8";
	addAttr -ci true -sn "happy" -ln "happy" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "angry" -ln "angry" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "sad" -ln "sad" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "surprise" -ln "surprise" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "fear" -ln "fear" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "disgust" -ln "disgust" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "contempt" -ln "contempt" -min 0 -max 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ovc" 17;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 0 2.9442166460922771e-17 ;
	setAttr ".sp" -type "double3" 0 0 2.9442166460922771e-17 ;
	setAttr -k on ".happy" 10;
	setAttr -k on ".angry";
	setAttr -k on ".sad";
	setAttr -k on ".surprise";
	setAttr -k on ".fear";
	setAttr -k on ".disgust";
	setAttr -k on ".contempt";
createNode nurbsCurve -n "M_Expression_A_ctrlShape" -p "M_Expression_A_ctrl";
	rename -uid "32EC62E2-467A-A4BE-D319-2EA165F8504E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		-0.31831796482089098 0.59748081172129308 -5.7626511127626669e-17
		-0.15202542812220654 0.65552880305464201 9.2977412352923682e-33
		-0.036508276611925607 0.5225680390433356 5.7626511127626595e-17
		-0.039434890958060187 0.27648513198170788 8.1496193588933549e-17
		-0.15909090016848343 0.061432111358262813 5.7626511127626595e-17
		-0.32538343686716636 0.0033841200249134923 2.4556393617704532e-32
		-0.44090058837744894 0.13634488403621964 -5.762651112762657e-17
		-0.43797397403131266 0.38242779109784641 -8.1496193588933549e-17
		-0.31831796482089098 0.59748081172129308 -5.7626511127626669e-17
		-0.15202542812220654 0.65552880305464201 9.2977412352923682e-33
		-0.036508276611925607 0.5225680390433356 5.7626511127626595e-17
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape1" -p "M_Expression_A_ctrl";
	rename -uid "39D272EB-401E-F704-6249-E9848F27A31E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		-0.15923641532934329 0.50898503089680169 -9.0062424051427679e-18
		-0.12645926909028266 0.5194675580795215 1.453110898903444e-33
		-0.09587006066182624 0.50370288176081202 9.0062424051427633e-18
		-0.085387533479106742 0.47092573552175077 1.2736750155372615e-17
		-0.10115220979781635 0.44033652709329552 9.0062424051427633e-18
		-0.13392935603687714 0.42985399991057549 3.8378313937371453e-33
		-0.1645185644653335 0.44561867622928519 -9.0062424051427633e-18
		-0.175001091648053 0.47839582246834533 -1.2736750155372615e-17
		-0.15923641532934329 0.50898503089680169 -9.0062424051427679e-18
		-0.12645926909028266 0.5194675580795215 1.453110898903444e-33
		-0.09587006066182624 0.50370288176081202 9.0062424051427633e-18
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape2" -p "M_Expression_A_ctrl";
	rename -uid "78A98E96-448E-3AAC-D57C-F6A53CBEFAB5";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		-0.2863561835315469 0.54379395669823904 -3.082027237460844e-17
		-0.17242901439161656 0.57360654560242819 4.9726924593038711e-33
		-0.070789656752505592 0.51412855552107461 3.0820272374608428e-17
		-0.040977067848316062 0.40020138638114511 4.358644718820414e-17
		-0.10045505792966891 0.29856202874203497 3.0820272374608428e-17
		-0.21438222706960025 0.26874943983784427 1.3133447176067534e-32
		-0.3160215847087105 0.32822742991919701 -3.0820272374608428e-17
		-0.34583417361289998 0.44215459905912657 -4.358644718820414e-17
		-0.2863561835315469 0.54379395669823904 -3.082027237460844e-17
		-0.17242901439161656 0.57360654560242819 4.9726924593038711e-33
		-0.070789656752505592 0.51412855552107461 3.0820272374608428e-17
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape3" -p "M_Expression_A_ctrl";
	rename -uid "E697C51A-4497-A57B-172C-68BDC5304969";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.067163129364247648 0.53491464163361424 -0.0016610503359698013
		0.19023662061406427 0.65862308094299271 -0.012171277223472526
		0.35095936811257333 0.58993975894693662 -0.015653631330065913
		0.45518216615701795 0.36909843416189936 -0.010068196849093422
		0.44185271316143243 0.125464959514512 0.0013131544522377511
		0.31877922191161728 0.0017565202051335049 0.011823381339740414
		0.15805647441310589 0.070439842201188374 0.015305735446333952
		0.053833676368664624 0.29128116698622658 0.0097203009653612921
		0.067163129364247648 0.53491464163361424 -0.0016610503359698013
		0.19023662061406427 0.65862308094299271 -0.012171277223472526
		0.35095936811257333 0.58993975894693662 -0.015653631330065913
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape4" -p "M_Expression_A_ctrl";
	rename -uid "B61521AA-42CC-49A7-4F04-E7BEF1385742";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.13759037650631364 0.51826893025025844 -0.0037854005109218512
		0.16995054028878309 0.52375907694162072 -0.0053460328207025273
		0.19675672332758237 0.50475576119594501 -0.0055910338162226125
		0.20230622715403834 0.47239086764698957 -0.0043768852371013495
		0.18334822769105441 0.44562331199097116 -0.0024148188542519392
		0.15098806390858477 0.44013316529960811 -0.00085418654447122488
		0.12418188086978554 0.45913648104528415 -0.00060918554895115357
		0.11863237704332966 0.4915013745942397 -0.001823334128072427
		0.13759037650631364 0.51826893025025844 -0.0037854005109218512
		0.16995054028878309 0.52375907694162072 -0.0053460328207025273
		0.19675672332758237 0.50475576119594501 -0.0055910338162226125
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape5" -p "M_Expression_A_ctrl";
	rename -uid "341A5F0F-4017-D5A9-0840-45A84B996162";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.1349906849524653 0.55098254852361772 -0.0051350590361476101
		0.25096384638074098 0.57065827305895556 -0.010728092001278222
		0.34703251320617629 0.50255371649797498 -0.011606132674821745
		0.36692096332153273 0.38656360441469384 -0.0072548367385316045
		0.29897881238381502 0.29063337136632161 -0.00022313433798757526
		0.18300565095553806 0.27095764683098178 0.0053698986271431721
		0.086936984130103701 0.33906220339196191 0.0062479393006866744
		0.067048534014747224 0.45505231547524305 0.0018966433643965407
		0.1349906849524653 0.55098254852361772 -0.0051350590361476101
		0.25096384638074098 0.57065827305895556 -0.010728092001278222
		0.34703251320617629 0.50255371649797498 -0.011606132674821745
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape6" -p "M_Expression_A_ctrl";
	rename -uid "56C01875-49E6-C784-6C3C-068B011ED11B";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 16 2 no 3
		21 -2 -1 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18
		19
		-0.29766547699238161 -0.26277704986213268 -5.5215307692333701e-17
		-0.00092835579729038569 -0.24227232439203422 -2.6572779533324638e-18
		0.29580876539780093 -0.26277704986213268 -5.5215307692333707e-17
		0.55670743014104196 -0.064552944894587905 -9.9771853843298225e-17
		0.4422480922064464 0.034233121704251974 -1.288472232229124e-16
		0.58476582252925424 -0.033395649163849753 -1.4069439121895913e-16
		0.66978490226346721 -0.16747046432256465 -1.288472232229122e-16
		0.55499761540305015 -0.063287408893725514 -9.9771853843298213e-17
		0.34259443697914477 -0.40816040310591489 -5.5215307692333774e-17
		-0.00092835579729038677 -0.69443956357438519 -2.6572779533323837e-18
		-0.34445114857372544 -0.40816040310591489 -5.5215307692333768e-17
		-0.58058558506350078 -0.064580819708496648 -9.9771853843298225e-17
		-0.69007270705287782 -0.17177106405258147 -1.288472232229122e-16
		-0.60969006526020064 -0.034520918785520119 -1.4069439121895913e-16
		-0.46957635225997518 0.038533721434268781 -1.2884722322291235e-16
		-0.57892012889578359 -0.063250486320812704 -9.9771853843298213e-17
		-0.29766547699238161 -0.26277704986213268 -5.5215307692333701e-17
		-0.00092835579729038569 -0.24227232439203422 -2.6572779533324638e-18
		0.29580876539780093 -0.26277704986213268 -5.5215307692333707e-17
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape7" -p "M_Expression_A_ctrl";
	rename -uid "01BD2988-47F3-1F81-63E9-F09986B36F80";
	setAttr -k off ".v" no;
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 13 0 no 3
		18 0 0 0 1 2 3 4 5 6 7 8 9 10 11 12 13 13 13
		16
		0.11538542920747033 0.73469472726588636 0
		0.11538542920747033 0.73469472726588636 0
		0.11538542920747033 0.73469472726588636 0
		0.11538542920747033 0.67624562825186763 0
		0.11538542920747033 0.67624562825186763 0
		0.11538542920747033 0.67624562825186763 0
		0.17265492532435783 0.67796978343556669 0
		0.26761736906421113 0.64532307807945077 0
		0.32311481428099548 0.59683869601124151 0
		0.32311481428099548 0.59683869601124151 0
		0.33920742839651968 0.60475848838762891 0
		0.35237028576210661 0.61381663909900896 0
		0.35237028576210661 0.61381663909900896 0
		0.28842124620322085 0.69522045254594089 0
		0.16880254751653298 0.73567111332032065 0
		0.11538542920747033 0.73469472726588636 0
		;
createNode nurbsCurve -n "M_Expression_A_ctrlShape8" -p "M_Expression_A_ctrl";
	rename -uid "7F66C6F8-4CBD-9999-9FFE-6B98E1D377E5";
	setAttr -k off ".v" no;
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 13 0 no 3
		18 0 0 0 1 2 3 4 5 6 7 8 9 10 11 12 13 13 13
		16
		-0.09583972781903638 0.7268328037328593 0
		-0.09583972781903638 0.7268328037328593 0
		-0.09583972781903638 0.7268328037328593 0
		-0.09583972781903638 0.66350861017090557 0
		-0.09583972781903638 0.66350861017090557 0
		-0.09583972781903638 0.66350861017090557 0
		-0.15310922393592388 0.66523276535460463 0
		-0.24847792555477194 0.63014851272452121 0
		-0.31616310714139401 0.56541381549652847 0
		-0.31616310714139401 0.56541381549652847 0
		-0.33225572125691821 0.57333360787291587 0
		-0.34704361013848345 0.58157924282630669 0
		-0.34704361013848345 0.58157924282630669 0
		-0.27659444451568421 0.6674518929421791 0
		-0.15250690916005574 0.72618415827131533 0
		-0.09583972781903638 0.7268328037328593 0
		;
createNode transform -n "L_Brow_A_ctrl_grp" -p "MFacePlanes";
	rename -uid "D2471D95-4901-277E-FFE5-25ABBF33E684";
	setAttr ".t" -type "double3" 20.467502600455511 162.43581133617499 12.430766582401663 ;
	setAttr ".s" -type "double3" 2.3199 2.3199 2.3199 ;
createNode transform -n "L_Brow_A_ctrl_zero" -p "L_Brow_A_ctrl_grp";
	rename -uid "4CD2094D-40A3-FE6C-AD66-CDBEA1678D5B";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "L_Brow_UD" -ln "L_Brow_UD" -at "double";
	addAttr -ci true -sn "L_Brow_LR" -ln "L_Brow_LR" -at "double";
	addAttr -ci true -sn "L_Brow_FB" -ln "L_Brow_FB" -at "double";
	addAttr -ci true -sn "L_Brow_RUD" -ln "L_Brow_RUD" -at "double";
	addAttr -ci true -sn "L_Brow_Twist" -ln "L_Brow_Twist" -at "double";
	addAttr -ci true -sn "L_BrowEyelid_UpUD" -ln "L_BrowEyelid_UpUD" -at "double";
	addAttr -ci true -sn "L_BrowEyelid_DownUD" -ln "L_BrowEyelid_DownUD" -at "double";
	addAttr -ci true -sn "L_BrowRing_UpUD" -ln "L_BrowRing_UpUD" -at "double";
	addAttr -ci true -sn "L_BrowRing_DownUD" -ln "L_BrowRing_DownUD" -at "double";
	addAttr -ci true -sn "LR_Brow_UD" -ln "LR_Brow_UD" -at "double";
	addAttr -ci true -sn "LR_Brow_LR" -ln "LR_Brow_LR" -at "double";
	addAttr -ci true -sn "LR_Brow_Twist" -ln "LR_Brow_Twist" -at "double";
	addAttr -ci true -sn "LR_Brow_RUD" -ln "LR_Brow_RUD" -at "double";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	setAttr -l on -k on "._";
	setAttr -k on ".L_Brow_UD";
	setAttr -k on ".L_Brow_LR";
	setAttr -k on ".L_Brow_FB";
	setAttr -k on ".L_Brow_RUD";
	setAttr -k on ".L_Brow_Twist";
	setAttr -k on ".L_BrowEyelid_UpUD";
	setAttr -k on ".L_BrowEyelid_DownUD";
	setAttr -k on ".L_BrowRing_UpUD";
	setAttr -k on ".L_BrowRing_DownUD";
	setAttr -k on ".LR_Brow_UD";
	setAttr -k on ".LR_Brow_LR";
	setAttr -k on ".LR_Brow_Twist";
	setAttr -k on ".LR_Brow_RUD";
	setAttr -l on -k on ".__";
createNode transform -n "L_Brow_A_ctrl" -p "L_Brow_A_ctrl_zero";
	rename -uid "3F4669F3-4DA5-67FB-247E-02A2F449D886";
	addAttr -ci true -sn "real_rz" -ln "real_rz" -min -180 -max 180 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr ".mrze" yes;
	setAttr ".xrze" yes;
	setAttr -cb on ".real_rz";
createNode nurbsCurve -n "L_Brow_A_ctrlShape" -p "L_Brow_A_ctrl";
	rename -uid "9E2550D4-4D17-FAFF-3A71-E890B6075AD8";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovrgbf" yes;
	setAttr ".ovc" 6;
	setAttr ".ovrgb" -type "float3" 0 0 1 ;
	setAttr ".cc" -type "nurbsCurve" 
		3 16 2 no 3
		21 -0.125 -0.0625 0 0.0625 0.125 0.1875 0.25 0.3125 0.375 0.43749999999999994
		 0.5 0.5625 0.625 0.6875 0.75 0.8125 0.87499999999999989 0.9375 1 1.0625 1.125
		19
		-1.3015908867569024 -0.29433258629259695 0
		-1.3015908867569024 -0.29433258629259695 0
		-1.3015908867569024 -0.29433258629259695 0
		-1.3015908867569024 -0.00041523953063365342 0
		-1.3015908867569024 0.2875634331786317 0
		-1.3015908867569024 0.2875634331786317 0
		-1.3015908867569024 0.2875634331786317 0
		5.7296291057570605e-15 0.2875634331786317 0
		1.3015908867569024 0.2875634331786317 0
		1.3015908867569024 0.2875634331786317 0
		1.3015908867569024 0.2875634331786317 0
		1.3015908867569024 -0.00041523953063365342 0
		1.3015908867569024 -0.29433258629259695 0
		1.3015908867569024 -0.29433258629259695 0
		1.3015908867569024 -0.29433258629259695 0
		5.7296291057570605e-15 -0.29433258629259695 0
		-1.3015908867569024 -0.29433258629259695 0
		-1.3015908867569024 -0.29433258629259695 0
		-1.3015908867569024 -0.29433258629259695 0
		;
createNode transform -n "R_Brow_A_ctrl_grp" -p "MFacePlanes";
	rename -uid "3603B8B9-4840-6B63-F035-DE9C5903C711";
	setAttr ".t" -type "double3" 9.9123859156902707 162.43581133617499 12.430766582401663 ;
	setAttr ".r" -type "double3" 0 180 0 ;
	setAttr ".s" -type "double3" 2.3199 2.3199 -2.3199 ;
createNode transform -n "R_Brow_A_ctrl_zero" -p "R_Brow_A_ctrl_grp";
	rename -uid "32FB1C49-4784-C1EC-A85A-0FB05B4B3E3A";
	addAttr -ci true -sn "_" -ln "_" -min 0 -max 0 -en "Handle" -at "enum";
	addAttr -ci true -sn "__" -ln "__" -min 0 -max 0 -en "Value" -at "enum";
	setAttr -l on -k on "._";
	setAttr -l on -k on ".__";
createNode transform -n "R_Brow_A_ctrl" -p "R_Brow_A_ctrl_zero";
	rename -uid "58F14E3B-48D4-D485-E4C8-7BA5CEE6BF47";
	addAttr -ci true -sn "real_rz" -ln "real_rz" -min -180 -max 180 -at "double";
	setAttr -l on -k off ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mtxe" yes;
	setAttr ".mtye" yes;
	setAttr ".mtze" yes;
	setAttr ".xtxe" yes;
	setAttr ".xtye" yes;
	setAttr ".xtze" yes;
	setAttr ".mnrl" -type "double3" -45 -45 -29.999999999999996 ;
	setAttr ".mxrl" -type "double3" 45 45 29.999999999999996 ;
	setAttr ".mrze" yes;
	setAttr ".xrze" yes;
	setAttr -cb on ".real_rz";
createNode nurbsCurve -n "R_Brow_A_ctrlShape" -p "R_Brow_A_ctrl";
	rename -uid "8A2175EF-476A-567D-AAE2-3D88399FEC4E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovrgbf" yes;
	setAttr ".ovc" 13;
	setAttr ".ovrgb" -type "float3" 1 0 0 ;
	setAttr ".cc" -type "nurbsCurve" 
		3 16 2 no 3
		21 -0.125 -0.0625 0 0.0625 0.125 0.1875 0.25 0.3125 0.375 0.43749999999999994
		 0.5 0.5625 0.625 0.6875 0.75 0.8125 0.87499999999999989 0.9375 1 1.0625 1.125
		19
		-1.3015908867569026 -0.2943325862925974 -8.8817841970012523e-16
		-1.3015908867569026 -0.2943325862925974 -8.8817841970012523e-16
		-1.3015908867569026 -0.2943325862925974 -8.8817841970012523e-16
		-1.3015908867569026 -0.00041523953063915542 -8.8817841970012523e-16
		-1.3015908867569026 0.28756343317863298 -8.8817841970012523e-16
		-1.3015908867569026 0.28756343317863298 -8.8817841970012523e-16
		-1.3015908867569026 0.28756343317863298 -8.8817841970012523e-16
		5.3290705182007514e-15 0.28756343317861877 -8.8817841970012523e-16
		1.3015908867569026 0.28756343317861877 -8.8817841970012523e-16
		1.3015908867569026 0.28756343317861877 -8.8817841970012523e-16
		1.3015908867569026 0.28756343317861877 -8.8817841970012523e-16
		1.3015908867569026 -0.00041523953065336627 -8.8817841970012523e-16
		1.3015908867569026 -0.29433258629261161 -8.8817841970012523e-16
		1.3015908867569026 -0.29433258629261161 -8.8817841970012523e-16
		1.3015908867569026 -0.29433258629261161 -8.8817841970012523e-16
		5.3290705182007514e-15 -0.29433258629261161 -8.8817841970012523e-16
		-1.3015908867569026 -0.2943325862925974 -8.8817841970012523e-16
		-1.3015908867569026 -0.2943325862925974 -8.8817841970012523e-16
		-1.3015908867569026 -0.2943325862925974 -8.8817841970012523e-16
		;
createNode unitConversion -n "unitConversion1303";
	rename -uid "20A4E239-4660-12F4-48B1-BEBB96382C8A";
	setAttr ".cf" 57.295779513082323;
createNode quatToEuler -n "QuaToEuler01_L_Brow_A_ctrl_real_rz";
	rename -uid "44A334B3-4DC6-C692-E1E0-6EB3920E5FCC";
	setAttr ".iro" 2;
createNode quatNormalize -n "QuaNor01_L_Brow_A_ctrl_real_rz";
	rename -uid "EF52A4C7-4ED1-0876-6D85-8B9388C7FAED";
createNode multiplyDivide -n "Mul01_L_Brow_A_ctrl_real_rz";
	rename -uid "88956691-46FB-8104-4D4B-70B0D655C335";
	setAttr ".i1" -type "float3" 0 0 1 ;
createNode blendWeighted -n "Dot01_L_Brow_A_ctrl_real_rz";
	rename -uid "6C3EA3D3-41E8-7A23-9512-D7A287DD9DFE";
	addAttr -ci true -h true -sn "aal" -ln "attributeAliasList" -dt "attributeAlias";
	setAttr -s 2 ".i[2:3]"  1 0;
	setAttr -s 2 ".w";
	setAttr -s 2 ".w";
	setAttr ".aal" -type "attributeAlias" 12 "dot00V" "input[0]" "dot01V" "input[1]" "dot02V" "input[2]" "dot03V" "input[3]" "dot02W" "weight[2]" "dot03W" "weight[3]" ;
createNode decomposeMatrix -n "MatToQua01_L_Brow_A_ctrl_real_rz";
	rename -uid "8D6F4A03-4E2E-5FD7-0E78-DA9126A9EBBF";
createNode unitConversion -n "unitConversion1304";
	rename -uid "843D4ED0-46B4-2DD5-ED96-648AFE631E13";
	setAttr ".cf" 57.295779513082323;
createNode quatToEuler -n "QuaToEuler01_R_Brow_A_ctrl_real_rz";
	rename -uid "E7394705-4F0B-09CE-B83D-46B9B5AC1BFA";
	setAttr ".iro" 2;
createNode quatNormalize -n "QuaNor01_R_Brow_A_ctrl_real_rz";
	rename -uid "EA9F0D90-4FBA-7A65-3812-44B5D1F673C6";
createNode multiplyDivide -n "Mul01_R_Brow_A_ctrl_real_rz";
	rename -uid "AAE1778D-44D3-CFFA-BB5A-33AD67AF768B";
	setAttr ".i1" -type "float3" 0 0 1 ;
createNode blendWeighted -n "Dot01_R_Brow_A_ctrl_real_rz";
	rename -uid "B6A5DFA2-4929-9929-0D82-389326D56268";
	addAttr -ci true -h true -sn "aal" -ln "attributeAliasList" -dt "attributeAlias";
	setAttr -s 2 ".i[2:3]"  1 0;
	setAttr -s 2 ".w";
	setAttr -s 2 ".w";
	setAttr ".aal" -type "attributeAlias" 12 "dot00V" "input[0]" "dot01V" "input[1]" "dot02V" "input[2]" "dot03V" "input[3]" "dot02W" "weight[2]" "dot03W" "weight[3]" ;
createNode decomposeMatrix -n "MatToQua01_R_Brow_A_ctrl_real_rz";
	rename -uid "285BB5BF-4B6E-8AFD-5EC4-B2B78A921672";
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 0;
	setAttr -av -k on ".unw";
	setAttr -av -k on ".etw";
	setAttr -av -k on ".tps";
	setAttr -av -k on ".tms";
select -ne :hardwareRenderingGlobals;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".fzn";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k on ".rm";
	setAttr -av -k on ".lm";
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr -av -k on ".hom";
	setAttr -av -k on ".hodm";
	setAttr -av -k on ".xry";
	setAttr -av -k on ".jxr";
	setAttr -av -k on ".sslt";
	setAttr -av -k on ".cbr";
	setAttr -av -k on ".bbr";
	setAttr -av -k on ".mhl";
	setAttr -av -k on ".cons";
	setAttr -av -k on ".vac";
	setAttr -av -k on ".hwi";
	setAttr -av -k on ".csvd";
	setAttr -av -k on ".ta";
	setAttr -av -k on ".tq";
	setAttr -av -k on ".ts";
	setAttr -av -k on ".etmr";
	setAttr -k on ".tmrm" 1;
	setAttr -av -k on ".tmr";
	setAttr -av -k on ".aoon";
	setAttr -av -k on ".aoam";
	setAttr -av -k on ".aora";
	setAttr -av -k on ".aofr";
	setAttr -av -k on ".aosm";
	setAttr -av -k on ".hff";
	setAttr -av -k on ".hfd";
	setAttr -av -k on ".hfs";
	setAttr -av -k on ".hfe";
	setAttr -av ".hfc";
	setAttr -av -k on ".hfcr";
	setAttr -av -k on ".hfcg";
	setAttr -av -k on ".hfcb";
	setAttr -av -k on ".hfa";
	setAttr -av -k on ".mbe";
	setAttr -av -k on ".mbt";
	setAttr -av -k on ".mbsof";
	setAttr -av -k on ".mbsc";
	setAttr -av -k on ".mbc";
	setAttr -av -k on ".mbfa";
	setAttr -av -k on ".mbftb";
	setAttr -av -k on ".mbftg";
	setAttr -av -k on ".mbftr";
	setAttr -av -k on ".mbfta";
	setAttr -av -k on ".mbfe";
	setAttr -av -k on ".mbme";
	setAttr -av -k on ".mbcsx";
	setAttr -av -k on ".mbcsy";
	setAttr -av -k on ".mbasx";
	setAttr -av -k on ".mbasy";
	setAttr -av -k on ".blen";
	setAttr -av -k on ".blth";
	setAttr -av -k on ".blfr";
	setAttr -av -k on ".blfa";
	setAttr -av -k on ".blat";
	setAttr -av -k on ".msaa" yes;
	setAttr -av -k on ".aasc";
	setAttr -av -k on ".aasq";
	setAttr -av -k on ".laa";
	setAttr -k on ".gamm";
	setAttr -av -k on ".gmmv";
	setAttr -av -k on ".fprt" yes;
	setAttr -av -k on ".rtfm" 1;
select -ne :renderPartition;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -s 28 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 31 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 22 ".u";
select -ne :defaultRenderingList1;
	setAttr -av -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultTextureList1;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 30 ".tx";
select -ne :standardSurface1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :initialShadingGroup;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -s 78 ".dsm";
	setAttr -k on ".mwc";
	setAttr -av -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
	setAttr -s 61 ".gn";
	setAttr -k on ".hio";
	setAttr -cb on ".ai_override";
	setAttr -k on ".ai_surface_shader";
	setAttr -cb on ".ai_surface_shaderr";
	setAttr -cb on ".ai_surface_shaderg";
	setAttr -cb on ".ai_surface_shaderb";
	setAttr -k on ".ai_volume_shader";
	setAttr -cb on ".ai_volume_shaderr";
	setAttr -cb on ".ai_volume_shaderg";
	setAttr -cb on ".ai_volume_shaderb";
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -k on ".mwc";
	setAttr -av -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
	setAttr -k on ".hio";
	setAttr -cb on ".ai_override";
	setAttr -k on ".ai_surface_shader";
	setAttr -cb on ".ai_surface_shaderr";
	setAttr -cb on ".ai_surface_shaderg";
	setAttr -cb on ".ai_surface_shaderb";
	setAttr -k on ".ai_volume_shader";
	setAttr -cb on ".ai_volume_shaderr";
	setAttr -cb on ".ai_volume_shaderg";
	setAttr -cb on ".ai_volume_shaderb";
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr -av -k on ".cch";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k on ".macc";
	setAttr -av -k on ".macd";
	setAttr -av -k on ".macq";
	setAttr -av -k on ".mcfr";
	setAttr -cb on ".ifg";
	setAttr -av -k on ".clip";
	setAttr -av -k on ".edm";
	setAttr -av -k on ".edl";
	setAttr -av -cb on ".ren" -type "string" "arnold";
	setAttr -av -k on ".esr";
	setAttr -av -k on ".ors";
	setAttr -cb on ".sdf";
	setAttr -av -k on ".outf" 51;
	setAttr -av -cb on ".imfkey" -type "string" "exr";
	setAttr -av -k on ".gama";
	setAttr -av -k on ".exrc";
	setAttr -av -k on ".expt";
	setAttr -av -k on ".an";
	setAttr -cb on ".ar";
	setAttr -av -k on ".fs";
	setAttr -av -k on ".ef";
	setAttr -av -k on ".bfs";
	setAttr -av -cb on ".me";
	setAttr -cb on ".se";
	setAttr -av -k on ".be";
	setAttr -av -cb on ".ep";
	setAttr -av -k on ".fec";
	setAttr -av -k on ".ofc";
	setAttr -cb on ".ofe";
	setAttr -cb on ".efe";
	setAttr -cb on ".oft";
	setAttr -cb on ".umfn";
	setAttr -cb on ".ufe";
	setAttr -av -k on ".pff";
	setAttr -av -cb on ".peie";
	setAttr -av -k on ".ifp";
	setAttr -av -k on ".rv";
	setAttr -av -k on ".comp";
	setAttr -av -k on ".cth";
	setAttr -av -k on ".soll";
	setAttr -av -cb on ".sosl";
	setAttr -av -k on ".rd";
	setAttr -av -k on ".lp";
	setAttr -av -k on ".sp";
	setAttr -av -k on ".shs";
	setAttr -av -k on ".lpr";
	setAttr -cb on ".gv";
	setAttr -cb on ".sv";
	setAttr -av -k on ".mm";
	setAttr -av -k on ".npu";
	setAttr -av -k on ".itf";
	setAttr -av -k on ".shp";
	setAttr -cb on ".isp";
	setAttr -av -k on ".uf";
	setAttr -av -k on ".oi";
	setAttr -av -k on ".rut";
	setAttr -av -k on ".mot";
	setAttr -av -cb on ".mb";
	setAttr -av -k on ".mbf";
	setAttr -av -k on ".mbso";
	setAttr -av -k on ".mbsc";
	setAttr -av -k on ".afp";
	setAttr -av -k on ".pfb";
	setAttr -av -k on ".pram";
	setAttr -av -k on ".poam";
	setAttr -av -k on ".prlm";
	setAttr -av -k on ".polm";
	setAttr -av -cb on ".prm";
	setAttr -av -cb on ".pom";
	setAttr -cb on ".pfrm";
	setAttr -cb on ".pfom";
	setAttr -av -k on ".bll";
	setAttr -av -k on ".bls";
	setAttr -av -k on ".smv";
	setAttr -av -k on ".ubc";
	setAttr -av -k on ".mbc";
	setAttr -cb on ".mbt";
	setAttr -av -k on ".udbx";
	setAttr -av -k on ".smc";
	setAttr -av -k on ".kmv";
	setAttr -cb on ".isl";
	setAttr -cb on ".ism";
	setAttr -cb on ".imb";
	setAttr -av -k on ".rlen";
	setAttr -av -k on ".frts";
	setAttr -av -k on ".tlwd";
	setAttr -av -k on ".tlht";
	setAttr -av -k on ".jfc";
	setAttr -cb on ".rsb";
	setAttr -av -k on ".ope";
	setAttr -av -k on ".oppf";
	setAttr -av -k on ".rcp";
	setAttr -av -k on ".icp";
	setAttr -av -k on ".ocp";
	setAttr -cb on ".hbl";
	setAttr ".dss" -type "string" "standardSurface1";
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".w" 2048;
	setAttr -av -k on ".h" 2048;
	setAttr -av -k on ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av -k on ".dar" 1;
	setAttr -av -k on ".ldar";
	setAttr -av -cb on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -av -cb on ".isu";
	setAttr -av -cb on ".pdu";
select -ne :defaultObjectSet;
	addAttr -ci true -sn "task_data" -ln "task_data" -dt "string";
	addAttr -ci true -sn "project" -ln "project" -dt "string";
	addAttr -ci true -sn "step" -ln "step" -dt "string";
	addAttr -ci true -sn "asset_type" -ln "asset_type" -dt "string";
	addAttr -ci true -sn "asset" -ln "asset" -dt "string";
	addAttr -ci true -sn "sequence" -ln "sequence" -dt "string";
	addAttr -ci true -sn "shot" -ln "shot" -dt "string";
	addAttr -ci true -sn "task" -ln "task" -dt "string";
	addAttr -ci true -sn "task_id" -ln "task_id" -at "long";
	addAttr -ci true -sn "status" -ln "status" -dt "string";
	addAttr -ci true -sn "task_type" -ln "task_type" -dt "string";
	addAttr -ci true -sn "tags" -ln "tags" -dt "string";
	addAttr -ci true -sn "start_frame" -ln "start_frame" -at "long";
	addAttr -ci true -sn "end_frame" -ln "end_frame" -at "long";
	addAttr -ci true -sn "width" -ln "width" -at "long";
	addAttr -ci true -sn "height" -ln "height" -at "long";
	addAttr -ci true -sn "assets" -ln "assets" -dt "string";
	addAttr -ci true -sn "simulation" -ln "simulation" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "motion_blur" -ln "motion_blur" -min 0 -max 1 -at "bool";
	setAttr -l on ".task_data" -type "string" (
		"{'type': 'Task', 'id': 20108, 'content': 'rigMaster', 'step': {'id': 15, 'name': 'rigging', 'type': 'Step'}, 'project': {'id': 386, 'name': 'ysj', 'type': 'Project'}, 'entity': {'id': 2965, 'name': 'yjTie', 'type': 'Asset'}, 'sg_status_list': 'tmapr', 'task_assignees': [{'id': 156, 'name': '余 炜铭', 'type': 'HumanUser'}], 'sg_description': '绑定阶段的主任务，用于提交可供动画制作使用的稳定绑定资产', 'tags': [], 'start_date': None, 'due_date': None, 'step.Step.short_name': 'rig', 'entity.Shot.code': None, 'entity.Shot.sg_sequence': None, 'entity.Shot.sg_sequence.Sequence.code': None, 'entity.Asset.code': 'yjTie', 'entity.Asset.sg_text': '杨戬铁匠装', 'entity.Asset.sg_asset_type': 'chr', 'entity.Asset.sg_list_1': None, 'entity.Shot.sg_cut_in': None, 'entity.Shot.sg_cut_out': None, 'entity.Shot.sg_simulation': None, 'entity.Shot.sg_motion_blur': None, 'entity.Shot.sg_shot_resolution': None, 'entity.Shot.assets': None, 'project.Project.sg_project_resolution': '2048*872', 'project.Project.sg_project_fps': 24, 'upstream_tasks': [], 'downstream_tasks': []}");
	setAttr -l on ".project" -type "string" "ysj";
	setAttr -l on ".step" -type "string" "rig";
	setAttr -l on ".asset_type" -type "string" "chr";
	setAttr -l on ".asset" -type "string" "yjTie";
	setAttr -l on ".sequence" -type "string" "";
	setAttr -l on ".shot" -type "string" "";
	setAttr -l on ".task" -type "string" "rigMaster";
	setAttr -l on ".task_id" 20108;
	setAttr -l on ".status" -type "string" "tmapr";
	setAttr -l on ".task_type" -type "string" "Asset";
	setAttr -l on ".tags" -type "string" "[]";
	setAttr -l on ".start_frame" 101;
	setAttr -l on ".end_frame" 102;
	setAttr -l on ".width";
	setAttr -l on ".height";
	setAttr -l on ".assets" -type "string" "[]";
	setAttr -l on ".simulation";
	setAttr -l on ".motion_blur";
select -ne :defaultColorMgtGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya-legacy/config.ocio";
	setAttr ".vtn" -type "string" "sRGB gamma (legacy)";
	setAttr ".vn" -type "string" "sRGB gamma";
	setAttr ".dn" -type "string" "legacy";
	setAttr ".wsn" -type "string" "scene-linear Rec 709/sRGB";
	setAttr ".otn" -type "string" "sRGB gamma (legacy)";
	setAttr ".potn" -type "string" "sRGB gamma (legacy)";
select -ne :hardwareRenderGlobals;
	setAttr -av -k on ".cch";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k off -cb on ".ctrs" 256;
	setAttr -av -k off -cb on ".btrs" 512;
	setAttr -av -k off -cb on ".fbfm";
	setAttr -av -k off -cb on ".ehql";
	setAttr -av -k off -cb on ".eams";
	setAttr -av -k off -cb on ".eeaa";
	setAttr -av -k off -cb on ".engm";
	setAttr -av -k off -cb on ".mes";
	setAttr -av -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -av -k off -cb on ".mbs";
	setAttr -av -k off -cb on ".trm";
	setAttr -av -k off -cb on ".tshc";
	setAttr -av -k off -cb on ".enpt";
	setAttr -av -k off -cb on ".clmt";
	setAttr -av -k off -cb on ".tcov";
	setAttr -av -k off -cb on ".lith";
	setAttr -av -k off -cb on ".sobc";
	setAttr -av -k off -cb on ".cuth";
	setAttr -av -k off -cb on ".hgcd";
	setAttr -av -k off -cb on ".hgci";
	setAttr -av -k off -cb on ".mgcs";
	setAttr -av -k off -cb on ".twa";
	setAttr -av -k off -cb on ".twz";
	setAttr -av -k on ".hwcc";
	setAttr -av -k on ".hwdp";
	setAttr -av -k on ".hwql";
	setAttr -av -k on ".hwfr";
	setAttr -av -k on ".soll";
	setAttr -av -k on ".sosl";
	setAttr -av -k on ".bswa";
	setAttr -av -k on ".shml";
	setAttr -av -k on ".hwel";
select -ne :ikSystem;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".gsn";
	setAttr -k on ".gsv";
	setAttr -s 4 ".sol";
connectAttr ":defaultHardwareRenderGlobals.msg" ":perspShape.b" -na;
connectAttr ":ikSystem.msg" ":perspShape.b" -na;
connectAttr "unitConversion1303.o" "L_Brow_A_ctrl.real_rz";
connectAttr "unitConversion1304.o" "R_Brow_A_ctrl.real_rz";
connectAttr "QuaToEuler01_L_Brow_A_ctrl_real_rz.orz" "unitConversion1303.i";
connectAttr "QuaNor01_L_Brow_A_ctrl_real_rz.oq" "QuaToEuler01_L_Brow_A_ctrl_real_rz.iq"
		;
connectAttr "Mul01_L_Brow_A_ctrl_real_rz.ox" "QuaNor01_L_Brow_A_ctrl_real_rz.iqx"
		;
connectAttr "Mul01_L_Brow_A_ctrl_real_rz.oy" "QuaNor01_L_Brow_A_ctrl_real_rz.iqy"
		;
connectAttr "Mul01_L_Brow_A_ctrl_real_rz.oz" "QuaNor01_L_Brow_A_ctrl_real_rz.iqz"
		;
connectAttr "MatToQua01_L_Brow_A_ctrl_real_rz.oqw" "QuaNor01_L_Brow_A_ctrl_real_rz.iqw"
		;
connectAttr "Dot01_L_Brow_A_ctrl_real_rz.o" "Mul01_L_Brow_A_ctrl_real_rz.i2x";
connectAttr "Dot01_L_Brow_A_ctrl_real_rz.o" "Mul01_L_Brow_A_ctrl_real_rz.i2y";
connectAttr "Dot01_L_Brow_A_ctrl_real_rz.o" "Mul01_L_Brow_A_ctrl_real_rz.i2z";
connectAttr "MatToQua01_L_Brow_A_ctrl_real_rz.oqz" "Dot01_L_Brow_A_ctrl_real_rz.w[2]"
		;
connectAttr "MatToQua01_L_Brow_A_ctrl_real_rz.oqw" "Dot01_L_Brow_A_ctrl_real_rz.w[3]"
		;
connectAttr "L_Brow_A_ctrl.m" "MatToQua01_L_Brow_A_ctrl_real_rz.imat";
connectAttr "QuaToEuler01_R_Brow_A_ctrl_real_rz.orz" "unitConversion1304.i";
connectAttr "QuaNor01_R_Brow_A_ctrl_real_rz.oq" "QuaToEuler01_R_Brow_A_ctrl_real_rz.iq"
		;
connectAttr "Mul01_R_Brow_A_ctrl_real_rz.ox" "QuaNor01_R_Brow_A_ctrl_real_rz.iqx"
		;
connectAttr "Mul01_R_Brow_A_ctrl_real_rz.oy" "QuaNor01_R_Brow_A_ctrl_real_rz.iqy"
		;
connectAttr "Mul01_R_Brow_A_ctrl_real_rz.oz" "QuaNor01_R_Brow_A_ctrl_real_rz.iqz"
		;
connectAttr "MatToQua01_R_Brow_A_ctrl_real_rz.oqw" "QuaNor01_R_Brow_A_ctrl_real_rz.iqw"
		;
connectAttr "Dot01_R_Brow_A_ctrl_real_rz.o" "Mul01_R_Brow_A_ctrl_real_rz.i2x";
connectAttr "Dot01_R_Brow_A_ctrl_real_rz.o" "Mul01_R_Brow_A_ctrl_real_rz.i2y";
connectAttr "Dot01_R_Brow_A_ctrl_real_rz.o" "Mul01_R_Brow_A_ctrl_real_rz.i2z";
connectAttr "MatToQua01_R_Brow_A_ctrl_real_rz.oqz" "Dot01_R_Brow_A_ctrl_real_rz.w[2]"
		;
connectAttr "MatToQua01_R_Brow_A_ctrl_real_rz.oqw" "Dot01_R_Brow_A_ctrl_real_rz.w[3]"
		;
connectAttr "R_Brow_A_ctrl.m" "MatToQua01_R_Brow_A_ctrl_real_rz.imat";
// End of plane.ma
