mode = 0;	// 0: assembly
				// 1: ball bearing
				// 2: base
				// 3: bearing block 1, print
				// 4: bearing block 2, print
				// 5: axle adapter, print
				// 6: spring limit, print
				// 7: knob
				
module ballbearing()
{
	difference()
	{
		cylinder(d=32, h=10);
		translate([0, 0, -1])
			cylinder(d=25, h=12);
	}
	difference()
	{
		cylinder(d=19, h=10);
		translate([0, 0, -1])
			cylinder(d=12, h=12);
	}
}


module base()
{
	difference()
	{
		cube([100,64,50]);
		translate([4, -1,4])
			cube([92, 100, 100]);
		
		// right bearing holes
		translate([95, 32, 50-22])
			rotate([0, 90, 0])
				cylinder(d=29, h=10);

		// screw holes right
		translate([95, 32+18, 50-22+18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);
		translate([95, 32+18, 50-22-18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);
		translate([95, 32-18, 50-22+18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);
		translate([95, 32-18, 50-22-18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);

		// left bearing holes
		translate([-5, 32, 50-22])
			rotate([0, 90, 0])
				cylinder(d=18, h=10);

		// screw holes left
		translate([-5, 32+18, 50-22+18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);
		translate([-5, 32+18, 50-22-18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);
		translate([-5, 32-18, 50-22+18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);
		translate([-5, 32-18, 50-22-18])
			rotate([0, 90, 0])
				cylinder(d=3.2, h=10);

		// screw holes bottom
		translate([50, 32, -1])
			cylinder(d=3.2, h=10);

	}
}

module axleadapter()
{
	difference()
	{
		union()
		{
			cylinder(d=12.2, h=15);
			cylinder(d=18, h=5);
		}
		translate([0, 0, -1])
			cylinder(d=10.6, h=100);
	}
}

module bearingblock1()
{
	difference()
	{
		translate([-22, -22, 0])
			cube([44,44,12]);
		translate([0, 0, 2])
			cylinder(d=32.2, h= 20);
		translate([0, 0, -1])
			cylinder(d=30, h= 20);
		// screws
		translate([18, 18, -1])
			cylinder(d=3.2, h= 20);
		translate([18, -18, -1])
			cylinder(d=3.2, h= 20);
		translate([-18, 18, -1])
			cylinder(d=3.2, h= 20);
		translate([-18, -18, -1])
			cylinder(d=3.2, h= 20);
		
	}
}

module bearingblock2()
{
	difference()
	{
		translate([-22, -22, 0])
			cube([44,44,12]);
		translate([0, 0, 2])
			cylinder(d=26.2, h= 20);
		translate([0, 0, -1])
			cylinder(d=18, h= 20);
		// screws
		translate([18, 18, -1])
			cylinder(d=3.2, h= 20);
		translate([18, -18, -1])
			cylinder(d=3.2, h= 20);
		translate([-18, 18, -1])
			cylinder(d=3.2, h= 20);
		translate([-18, -18, -1])
			cylinder(d=3.2, h= 20);
		
	}
}

module springlimit()
{
	difference()
	{
		cylinder(d=32, h=10);
		translate([0, 0, -1])
			cylinder(d=10.1, h=20);
		// screw hole front
		translate([0, 0, 5])
			rotate([90, 0, 0])
				cylinder(d=2.4, h=20);
		// screw hole right
		translate([0, 0, 5])
			rotate([0, 90, 0])
				cylinder(d=2.4, h=20);
	}
}

module knob()
{
	difference()
	{
		translate([0, 0, 14])
			sphere(d=36);
		translate([-50, -50, -100])
			cube([100,100,100]);
		translate([0,0,-1])
			cylinder(d=10.1, h=24);
		translate([0,0,14])
			rotate([90, 0, 0])
				cylinder(d=2.4, h=100);
	}
}
	
module assembly()
{
	translate([-50, -32, 0])
		base();
	
	translate([50-4-12, 0, 50-22])
		rotate([0, 90, 0])
			bearingblock1();
	
	translate([-50-12, 0, 50-22])
		rotate([0, 90, 0])
			bearingblock2();
	
	translate([70, 0, 50-22])
		rotate([0, 90, 0])
			knob();
	
	translate([20, 0, 50-22])
		rotate([0, 90, 0])
			axleadapter();

	translate([-30, 0, 50-22])
		rotate([0, 90, 0])
			springlimit();
}

if(mode==0)
{
	$fn=36;
	
	assembly();
}
else if(mode==1)
{
	$fn=24;
	
	ballbearing();
}
else if(mode==2)
{
	$fn = 24;

	base();
}
else if(mode==3)
{
	$fn = 4*60;

	bearingblock1();
}
else if(mode==4)
{
	$fn = 4*60;

	bearingblock2();
}
else if(mode==5)
{
	$fn = 4*60;

	axleadapter();
}
else if(mode==6)
{
	$fn = 4*60;

	springlimit();
}
else if(mode==7)
{
	$fn = 4*60;

	knob();
	
	/*
	difference()
	{
		knob();
		translate([-50,0,-1])
			cube([100,100,100]);
	}
	*/
}
