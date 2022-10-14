
title = getTitle();
getDimensions(W,H, C,Z,T);
frint = Stack.getFrameInterval();

setBatchMode(true);

for( t=1; t<=T; t++ ){
	channel1 = "C1";
	channel2 = "C2";
	run("Duplicate...", "title="+channel1+" duplicate channels=1 frames="+t);
	selectImage(title);
	run("Duplicate...", "title="+channel2+" duplicate channels=2 frames="+t);

	run("JACoP ", "imga="+channel1+" imgb="+channel2+" pearson");	//methods are: pearson overlap mm ccf=20 ica
	
	selectImage(channel1);
	close();
	selectImage(channel2);
	close();
}

txt = getInfo( "log" );
print("\\Clear");
lines = split(txt, "\n");
t = 0;
for(i=0;i<lines.length;i++){
	line = replace(lines[i], "\\'", "");
	if(startsWith(line, "r=")){
		line = replace(lines[i], "r=", "");
		row = nResults;
		//setResult("Image", row, title);
		setResult("Time (sec)", row, round(t*frint));
		setResult("Pearson\'s r", row, line);
		t++;
	}
}
updateResults();



setBatchMode("exit and display");