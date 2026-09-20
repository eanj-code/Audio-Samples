# Audio Samples

## Joint visual and attribute samples

Each subfolder of joint_cond becomes one sample row. Include sentence.txt, art.png (full artwork), and face.png (face only). Put one RVTTS clip in rvtts/, and the proposed-model audio files in face/ and full/. Supported audio formats are WAV, MP3, OGG, and M4A.

The table shows both visual inputs, the sentence, and three audio columns: RVTTS (face only), Proposed (face only), and Proposed (full artwork). Each Proposed column has an independent masculinity slider that selects files in natural filename order, from lowest to highest strength (0.wav is lowest). Moving a slider plays its selected clip. Missing media or sentences display a placeholder; more than one RVTTS clip is flagged as an error.

Optionally add remarks.txt in a sample folder to display a highlighted Remarks field beneath and across the two Proposed audio columns. Use the first line for the remark heading and the second line for its body. The table displays the heading in bold, followed by a colon and the body. Missing or empty remarks files produce no note.

After changing samples, run `python tools/update_joint_samples.py` from the repository root. Commit the updated HTML together with the sample files. The generated table works on static hosting and when opening the HTML directly. Run `python tools/update_joint_samples.py --check` to check that the table is current without writing.
