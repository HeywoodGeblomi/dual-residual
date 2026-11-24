#include "../core/dual_residual.hpp"
#include "../core/tests/generators.hpp"
#include <cstdio>
#include <random>
using namespace dual_residual_test;
int main(){ auto p=[](const char*n,std::vector<int64_t> a){auto e=dual_residual::evidence(a.data(),a.size());std::printf("%s conf=%d T=%d s=%.4f c=%.4f\n",n,e.confirmed,(int)e.suggested,e.sigma_delta,e.classical);};
 auto r=noisy_ramp_confirmed(); p("ramp",r); p("ramp_drop1",std::vector<int64_t>(r.begin()+1,r.end()));
 auto b=biased_walk_t2(); p("walk",b); p("walk_drop1",std::vector<int64_t>(b.begin()+1,b.end()));
 std::mt19937_64 g(1234); int tal[4]={0}; for(int k=0;k<500;++k){auto s=sorted(1024); for(auto&v:s) v+=(int64_t)(g()%3)-1; auto e=dual_residual::evidence(s.data(),s.size()); tal[(int)e.suggested]++;} std::printf("sorted+jitter talents None/T1/T2/T3 = %d/%d/%d/%d\n",tal[0],tal[1],tal[2],tal[3]);}
