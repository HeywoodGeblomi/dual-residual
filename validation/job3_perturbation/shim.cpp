#include "../core/dual_residual.hpp"
extern "C" void ev(const long long* a, unsigned long n, int* conf, int* tal, float* s, float* c){
 auto e=dual_residual::evidence((const int64_t*)a,(size_t)n); *conf=e.confirmed; *tal=(int)e.suggested; *s=e.sigma_delta; *c=e.classical; }
