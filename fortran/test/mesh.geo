S = 1e3;
L = 20e3;
W = 20e3;

Point(1) = {0, 0, 0, S};
Point(2) = {L, 0, 0, S};
Point(3) = {L, W, 0, S};
Point(4) = {0, W, 0, S};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

Line Loop(1) = {1, 2, 3, 4};

Plane Surface(1) = {1};

Physical Line(1) = {1};
Physical Line(2) = {2};
Physical Line(3) = {3};
Physical Line(4) = {4};

Physical Surface(1) = {1};
