// Job 3 perturbation suite. Measures decision stability of dual_residual::evidence
// under small perturbations. Core header included read-only; constants untouched.
#include "../core/dual_residual.hpp"
#include "../core/tests/generators.hpp"
#include <cstdio>
#include <vector>
#include <random>
#include <string>
#include <functional>
using namespace dual_residual_test;
using V = std::vector<int64_t>;
struct D { bool c; int t; float s; float k; };
static D ev(const V& a){ auto e=dual_residual::evidence(a.data(),a.size()); return {e.confirmed,(int)e.suggested,e.sigma_delta,e.classical}; }
static bool same(const D&x,const D&y){ return x.c==y.c && x.t==y.t; }
int main(){
  const int TR=500;
  std::vector<std::pair<std::string,V>> cases={
    {"noisy_ramp_confirmed",noisy_ramp_confirmed()},{"biased_walk_t2",biased_walk_t2()},
    {"pairwise_swapped",pairwise_swapped(1024)},{"alt_high_low",alt_high_low(1024)},
    {"block_zigzag",block_zigzag(1024)},{"moderate_local_disorder",moderate_local_disorder(1024)},
    {"sorted",sorted(1024)},{"reverse",reverse(1024)},{"equal_heavy",equal_heavy(1024)}};
  std::printf("case,base_conf,base_talent,base_sigma,base_classical,phase_drop1,phase_prepend1,insert1,delete1,jitter1,quant2,quant4,quant8\n");
  for(auto& [name,a]:cases){
    D b=ev(a); std::mt19937_64 rng(1234);
    auto rate=[&](std::function<V()> f,int n){int k=0;for(int i=0;i<n;++i) if(same(ev(f()),b))++k;return (double)k/n;};
    double p1=same(ev(V(a.begin()+1,a.end())),b);
    V pre=a; pre.insert(pre.begin(),a[0]); double p2=same(ev(pre),b);
    double ins=rate([&]{V x=a;size_t i=rng()%x.size();x.insert(x.begin()+i,x[i]+(int64_t)(rng()%21)-10);return x;},TR);
    double del=rate([&]{V x=a;x.erase(x.begin()+rng()%x.size());return x;},TR);
    double jit=rate([&]{V x=a;for(auto& v:x) v+=(int64_t)(rng()%3)-1;return x;},TR);
    auto q=[&](int s){V x=a;for(auto& v:x) v=(v>=0? v/s : -((-v+s-1)/s));return (double)same(ev(x),b);};
    std::printf("%s,%d,%d,%.6f,%.6f,%.0f,%.0f,%.3f,%.3f,%.3f,%.0f,%.0f,%.0f\n",name.c_str(),b.c,b.t,b.s,b.k,p1,p2,ins,del,jit,q(2),q(4),q(8));
  }
}
