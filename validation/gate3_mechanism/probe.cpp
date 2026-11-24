#include "dual_residual.hpp"
#include <random>
#include <cstdio>
#include <vector>
using namespace dual_residual;
// Quantized random walk with ties, like Job 2 rw_q
std::vector<int> walk(std::mt19937_64& g, size_t n, double tie) {
  std::vector<int> a(n); int x=0; std::uniform_real_distribution<double> u(0,1);
  for (size_t i=0;i<n;++i){ double r=u(g); if(r<tie){} else if(r<tie+(1-tie)/2) x++; else x--; a[i]=x; }
  return a;
}
int first_sign(const int* a, size_t n){ size_t s=(n>1024)?n/512:1; if(s<1)s=1; return (a[s]>a[0])?1:((a[s]<a[0])?-1:0); }
int main(){
  std::mt19937_64 g(12345);
  size_t Ns[]={64,256,1024,4096,16384};
  double ties[]={0.05,0.2,0.4};
  for(double tie: ties) for(size_t N: Ns){
    int trials=4000, firstNonPos=0, zeroSigmaWhenNonPos=0, firstPos=0, ownedWhenPos=0, ownedTotal=0, flips=0, flipsExplained=0;
    for(int k=0;k<trials;++k){
      auto a=walk(g,N+1,tie);
      Evidence e0=evidence(a.data(),N), e1=evidence(a.data()+1,N);
      int fs=first_sign(a.data(),N);
      if(fs<=0){ firstNonPos++; if(e0.sigma_delta==0.f) zeroSigmaWhenNonPos++; }
      else { firstPos++; if(e0.confirmed) ownedWhenPos++; }
      if(e0.confirmed) ownedTotal++;
      if(e0.suggested!=e1.suggested){ flips++; int fs1=first_sign(a.data()+1,N); if((fs>0)!=(fs1>0)) flipsExplained++; }
    }
    printf("tie=%.2f N=%5zu  first<=0: %d, of those sigma==0 exactly: %d | first>0: %d, owned: %d | owned overall %.3f | 1-sample flips %.3f, of which first-sign changed %.3f\n",
      tie,N,firstNonPos,zeroSigmaWhenNonPos,firstPos,ownedWhenPos,(double)ownedTotal/trials,(double)flips/trials, flips?(double)flipsExplained/flips:0.0);
  }
}
