// Reads one window per line (whitespace ints); prints tier sigma classical using the UNMODIFIED core header.
#include "dual_residual.hpp"
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <cstdio>
int main(){ std::string line; while(std::getline(std::cin,line)){ std::istringstream ss(line); std::vector<long long> a; long long v; while(ss>>v) a.push_back(v);
  auto e=dual_residual::evidence(a.data(),a.size()); std::printf("%d %.9g %.9g\n",(int)e.suggested,e.sigma_delta,e.classical);} }
