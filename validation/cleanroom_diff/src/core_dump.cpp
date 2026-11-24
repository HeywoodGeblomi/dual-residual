// Exploratory G4-04-style dump of the locked Dual Residual core at ba2ea57.
// Includes the core header only, unmodified. DS1 windows only for cache mode.
// Never reads DS2. Does not invoke the clean-room reference.
#include "ds1_io.hpp"
#include "dual_residual.hpp"
#include "dual_residual_prod.hpp"

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

static const char* tier_name(dual_residual::Talent t) {
    switch (t) {
        case dual_residual::Talent::T1: return "T1";
        case dual_residual::Talent::T2: return "T2";
        case dual_residual::Talent::T3: return "T3";
        case dual_residual::Talent::None:
        default: return "None";
    }
}

static void die(const std::string& msg) {
    std::cerr << "FATAL: " << msg << std::endl;
    std::exit(2);
}

// Diagnostic only: which path we will call, and whether the base core
// would early-return before filling features (n<2 or Tlen<4). Does not
// change the evidence() call.
static void describe(size_t n, const char** path, const char** status) {
    *path = "base";
    if (n == 0 || n > dual_residual::prod::kMaxReasonableN) {
        *path = "prod";
        *status = "guard_n";
        return;
    }
    if (n < 2) {
        *status = "early_n";
        return;
    }
    size_t stride = (n > 1024) ? (n / 512) : 1;
    if (stride < 1) stride = 1;
    int tlen = 0;
    for (size_t i = 0; i + stride < n && tlen < (int)DUAL_RESIDUAL_MAX_EVENTS; i += stride) {
        ++tlen;
    }
    *status = (tlen < 4) ? "early_tlen" : "ok";
}

template <typename T>
static dual_residual::Evidence run_core(const T* a, size_t n, const char** path,
                                        const char** status) {
    describe(n, path, status);
    if (std::strcmp(*path, "prod") == 0) {
        return dual_residual::prod::evidence(a, n);
    }
    return dual_residual::evidence(a, n);
}

static std::string json_str(const std::string& line, const std::string& key) {
    const std::string pat = "\"" + key + "\"";
    size_t pos = line.find(pat);
    if (pos == std::string::npos) return {};
    pos = line.find(':', pos + pat.size());
    if (pos == std::string::npos) return {};
    pos = line.find('"', pos + 1);
    if (pos == std::string::npos) return {};
    size_t end = line.find('"', pos + 1);
    if (end == std::string::npos) return {};
    return line.substr(pos + 1, end - pos - 1);
}

static bool json_ints(const std::string& line, std::vector<int32_t>& out) {
    const std::string pat = "\"values\"";
    size_t pos = line.find(pat);
    if (pos == std::string::npos) return false;
    pos = line.find('[', pos);
    size_t end = line.rfind(']');
    if (pos == std::string::npos || end == std::string::npos || end <= pos) return false;
    out.clear();
    const char* p = line.c_str() + pos + 1;
    const char* e = line.c_str() + end;
    while (p < e) {
        while (p < e && (*p == ' ' || *p == '\t' || *p == ',' || *p == '\n' || *p == '\r')) ++p;
        if (p >= e) break;
        char* next = nullptr;
        long v = std::strtol(p, &next, 10);
        if (next == p) return false;
        out.push_back(static_cast<int32_t>(v));
        p = next;
    }
    return true;
}

static int mode_ds1(const std::string& cache, const std::string& keys_path,
                    const std::string& out_path) {
    CacheMeta meta = load_meta(cache);
    auto sigs = load_all_ds1_signals(meta);

    std::ifstream kin(keys_path);
    if (!kin) die("cannot open keys file " + keys_path);
    std::string header;
    if (!std::getline(kin, header)) die("empty keys file " + keys_path);
    // Expect at least N,record,start as the first three columns of core_ds1_preds.csv
    if (header.find("N") == std::string::npos || header.find("record") == std::string::npos ||
        header.find("start") == std::string::npos) {
        die("keys file missing N,record,start columns: " + keys_path);
    }

    FILE* out = std::fopen(out_path.c_str(), "w");
    if (!out) die("cannot write " + out_path);
    std::fprintf(out, "N,record,window_start,core_tier,confirmed,classical,sigma_delta,path,status\n");

    std::string line;
    uint64_t n_rows = 0;
    int last_N = -1;
    uint64_t n_at_N = 0;
    while (std::getline(kin, line)) {
        if (line.empty()) continue;
        int N = 0, record = 0;
        unsigned int start = 0;
        if (std::sscanf(line.c_str(), "%d,%d,%u", &N, &record, &start) != 3) {
            die("bad keys row: " + line);
        }
        assert_ds1_record(meta, record, "core_dump_ds1");
        Window w;
        w.record = static_cast<uint16_t>(record);
        w.start = start;
        const int16_t* x = window_ptr(sigs, w, N);
        const char* path = "base";
        const char* status = "ok";
        const auto e = run_core(x, static_cast<size_t>(N), &path, &status);
        std::fprintf(out, "%d,%d,%u,%s,%d,%.9g,%.9g,%s,%s\n", N, record, start,
                     tier_name(e.suggested), e.confirmed ? 1 : 0, (double)e.classical,
                     (double)e.sigma_delta, path, status);
        ++n_rows;
        if (N != last_N) {
            if (last_N != -1) {
                std::cerr << "core_dump ds1 N=" << last_N << " windows=" << n_at_N << std::endl;
            }
            last_N = N;
            n_at_N = 0;
        }
        ++n_at_N;
    }
    if (last_N != -1) {
        std::cerr << "core_dump ds1 N=" << last_N << " windows=" << n_at_N << std::endl;
    }
    std::fclose(out);
    std::cerr << "core_dump ds1 total=" << n_rows << " -> " << out_path << std::endl;
    return 0;
}

static int mode_shift(const std::string& cache, const std::string& keys_path,
                      const std::string& out_path, int shift) {
    if (shift < 0) die("shift must be >= 0");
    CacheMeta meta = load_meta(cache);
    auto sigs = load_all_ds1_signals(meta);

    std::ifstream kin(keys_path);
    if (!kin) die("cannot open keys file " + keys_path);
    std::string header;
    if (!std::getline(kin, header)) die("empty keys file " + keys_path);

    FILE* out = std::fopen(out_path.c_str(), "w");
    if (!out) die("cannot write " + out_path);
    std::fprintf(out, "N,record,orig_start,window_start,core_tier,confirmed,classical,sigma_delta,path,status,skipped\n");

    std::string line;
    uint64_t n_ok = 0, n_skip = 0, n_considered = 0;
    while (std::getline(kin, line)) {
        if (line.empty()) continue;
        int N = 0, record = 0;
        unsigned int start = 0;
        if (std::sscanf(line.c_str(), "%d,%d,%u", &N, &record, &start) != 3) {
            die("bad keys row: " + line);
        }
        if (N != 1024 && N != 4096) continue;
        ++n_considered;
        assert_ds1_record(meta, record, "core_dump_shift");
        auto it = sigs.find(record);
        if (it == sigs.end()) die("missing signal for record");
        const Signal& s = it->second;
        const uint32_t shifted = start + static_cast<uint32_t>(shift);
        if (static_cast<int64_t>(shifted) + N > s.n_samples) {
            std::fprintf(out, "%d,%d,%u,%u,None,0,0,0,base,skip_oob,1\n", N, record, start,
                         shifted);
            ++n_skip;
            continue;
        }
        const int16_t* x = s.x.data() + shifted;
        const char* path = "base";
        const char* status = "ok";
        const auto e = run_core(x, static_cast<size_t>(N), &path, &status);
        std::fprintf(out, "%d,%d,%u,%u,%s,%d,%.9g,%.9g,%s,%s,0\n", N, record, start, shifted,
                     tier_name(e.suggested), e.confirmed ? 1 : 0, (double)e.classical,
                     (double)e.sigma_delta, path, status);
        ++n_ok;
    }
    std::fclose(out);
    std::cerr << "core_dump shift=" << shift << " considered=" << n_considered
              << " ok=" << n_ok << " skipped_oob=" << n_skip << " -> " << out_path << std::endl;
    return 0;
}

static int mode_edge(const std::string& edge_path, const std::string& out_path) {
    std::ifstream in(edge_path);
    if (!in) die("cannot open edge suite " + edge_path);
    FILE* out = std::fopen(out_path.c_str(), "w");
    if (!out) die("cannot write " + out_path);
    std::fprintf(out, "id,class,N,core_tier,confirmed,classical,sigma_delta,path,status\n");

    std::string line;
    uint64_t n_rows = 0, n_early = 0, n_prod = 0;
    std::vector<int32_t> values;
    values.reserve(16384);
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        const std::string id = json_str(line, "id");
        const std::string cls = json_str(line, "class");
        if (id.empty() || cls.empty() || !json_ints(line, values)) {
            die("bad jsonl line near row " + std::to_string(n_rows + 1));
        }
        const char* path = "base";
        const char* status = "ok";
        const auto e = run_core(values.data(), values.size(), &path, &status);
        std::fprintf(out, "%s,%s,%zu,%s,%d,%.9g,%.9g,%s,%s\n", id.c_str(), cls.c_str(),
                     values.size(), tier_name(e.suggested), e.confirmed ? 1 : 0,
                     (double)e.classical, (double)e.sigma_delta, path, status);
        ++n_rows;
        if (std::strcmp(status, "ok") != 0) ++n_early;
        if (std::strcmp(path, "prod") == 0) ++n_prod;
        if (n_rows % 10000 == 0) {
            std::cerr << "core_dump edge progress " << n_rows << std::endl;
        }
    }
    std::fclose(out);
    std::cerr << "core_dump edge total=" << n_rows << " early_or_guard=" << n_early
              << " prod_path=" << n_prod << " -> " << out_path << std::endl;
    return 0;
}

static int mode_txt_dir(const std::string& manifest_path, const std::string& root,
                        const std::string& out_path) {
    // Cheddar (or similar) manifest.csv: file,case,N,length,sha256,description
    std::ifstream man(manifest_path);
    if (!man) die("cannot open manifest " + manifest_path);
    std::string header;
    if (!std::getline(man, header)) die("empty manifest");
    FILE* out = std::fopen(out_path.c_str(), "w");
    if (!out) die("cannot write " + out_path);
    std::fprintf(out, "id,class,N,file,core_tier,confirmed,classical,sigma_delta,path,status\n");

    std::string line;
    uint64_t n_rows = 0;
    while (std::getline(man, line)) {
        if (line.empty()) continue;
        // parse first four comma-separated fields; file may not contain commas
        std::string file, casename, nstr, lenstr;
        std::stringstream ss(line);
        if (!std::getline(ss, file, ',') || !std::getline(ss, casename, ',') ||
            !std::getline(ss, nstr, ',') || !std::getline(ss, lenstr, ',')) {
            die("bad manifest row: " + line);
        }
        const std::string path_txt = root + "/" + file;
        std::ifstream in(path_txt);
        if (!in) die("cannot open case file " + path_txt);
        std::vector<int32_t> values;
        int32_t v;
        while (in >> v) values.push_back(v);
        if (values.empty()) die("empty case " + path_txt);
        const char* path = "base";
        const char* status = "ok";
        const auto e = run_core(values.data(), values.size(), &path, &status);
        std::fprintf(out, "%s,%s,%zu,%s,%s,%d,%.9g,%.9g,%s,%s\n", casename.c_str(),
                     casename.c_str(), values.size(), file.c_str(), tier_name(e.suggested),
                     e.confirmed ? 1 : 0, (double)e.classical, (double)e.sigma_delta, path,
                     status);
        ++n_rows;
    }
    std::fclose(out);
    std::cerr << "core_dump txt_dir total=" << n_rows << " -> " << out_path << std::endl;
    return 0;
}

static void usage() {
    std::cerr
        << "usage: core_dump --mode=ds1|shift|edge|txt_dir [options]\n"
        << "  --cache=DIR --keys=CSV --out=PATH --edge=JSONL --shift=K\n"
        << "  --manifest=CSV --root=DIR\n";
}

int main(int argc, char** argv) {
    std::string mode;
    std::string cache = "/workspace/toni/dual-residual-job4/cache";
    std::string keys = "/workspace/toni/dual-residual-job4/results/core_ds1_preds.csv";
    std::string out_path;
    std::string edge_path;
    std::string manifest;
    std::string root;
    int shift = 1;
    for (int i = 1; i < argc; ++i) {
        const char* a = argv[i];
        if (std::strncmp(a, "--mode=", 7) == 0) mode = a + 7;
        else if (std::strncmp(a, "--cache=", 8) == 0) cache = a + 8;
        else if (std::strncmp(a, "--keys=", 7) == 0) keys = a + 7;
        else if (std::strncmp(a, "--out=", 6) == 0) out_path = a + 6;
        else if (std::strncmp(a, "--edge=", 7) == 0) edge_path = a + 7;
        else if (std::strncmp(a, "--shift=", 8) == 0) shift = std::atoi(a + 8);
        else if (std::strncmp(a, "--manifest=", 11) == 0) manifest = a + 11;
        else if (std::strncmp(a, "--root=", 7) == 0) root = a + 7;
        else {
            std::cerr << "unknown arg " << a << std::endl;
            usage();
            return 2;
        }
    }
    if (out_path.empty() || mode.empty()) {
        usage();
        return 2;
    }
    if (mode == "ds1") return mode_ds1(cache, keys, out_path);
    if (mode == "shift") return mode_shift(cache, keys, out_path, shift);
    if (mode == "edge") {
        if (edge_path.empty()) die("--edge=PATH required");
        return mode_edge(edge_path, out_path);
    }
    if (mode == "txt_dir") {
        if (manifest.empty()) die("--manifest=PATH required");
        if (root.empty()) die("--root=DIR required");
        return mode_txt_dir(manifest, root, out_path);
    }
    die("unknown mode " + mode);
    return 2;
}
