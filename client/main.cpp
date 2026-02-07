#include <algorithm>
#include <array>
#include <cstring>
#include <iostream>
#include <memory>
#include <random>
#include <span>
#include <string>

#include <xatmi.h>

std::mt19937_64 rng;

using buffer_t = std::unique_ptr<char, decltype(&::tpfree)>;

auto create_buffer(std::span<const std::byte> payload)
{
    auto buffer = buffer_t(tpalloc(CASUAL_BUFFER_JSON_TYPE, 0, payload.size_bytes()), &::tpfree);
    std::memcpy(buffer.get(), payload.data(), payload.size_bytes());
    return buffer;
}

// takes an existing buffer as input, and stores response in an existing buffer
auto service_call(const std::string &service, const buffer_t& in, buffer_t& out, long flags)
{
    long ilen = tptypes(in.get(), nullptr, nullptr);
    long olen = tptypes(out.get(), nullptr, nullptr);
    char *odata = out.get();
    int rc = tpcall(service.c_str(), in.get(), ilen, &odata, &olen, flags);
    if (odata != out.get())
    {
        out.release();
        out.reset(odata);
    }
    return rc;
}

// returns a new buffer with response
auto service_call(const std::string &service, std::span<const std::byte> payload, long flags)
{
    long length = payload.size_bytes();
    auto buffer = std::unique_ptr<char, decltype(&::tpfree)>(tpalloc(CASUAL_BUFFER_JSON_TYPE, 0, length), &::tpfree);
    auto data = buffer.get();

    std::memcpy(buffer.get(), payload.data(), payload.size_bytes());

    auto rc = tpcall(service.c_str(), buffer.get(), length, &data, &length, flags);
    buffer.release();
    buffer.reset(data);
    return buffer;
}

void error_exit_usage(std::string_view msg)
{
    std::cerr << "Error: " << msg << std::endl;
    exit(1);
}

int main(int argc, char *argv[])
{
    std::vector<std::string> args{ argv, argv + argc};
    long long num_calls = 1000;
    long long payload_size = 1024;
    std::string service = "casual/example/echo";

    // fix: looking ahead in argument vector could crash on bad input
    for (int i = 1; i < args.size(); ++i)
    {
        const auto& arg = args[i];
        if (arg == "-n")
        {
            num_calls = std::stoll(args[++i]);
        }
        else if (arg == "-p")
        {
            payload_size = std::stoll(args[++i]);
        }
        else if (arg == "-s")
        {
            service = args[++i];
        }
        else
        {
            error_exit_usage("Unexpected argument");
        }
    }
    using payload_t = std::mt19937_64::result_type;
    auto elements = payload_size / sizeof(std::mt19937_64::result_type);
    auto payload_data = std::make_unique<payload_t[]>(elements);

    std::ranges::generate_n(payload_data.get(), elements, rng);
    auto payload = std::as_bytes(std::span(payload_data.get(), elements));

    auto input = create_buffer(payload);
    auto response = create_buffer(payload);;

    for (int i = 0; i < num_calls; ++i)
    {
        auto rc = service_call( service, input, response, TPNOTRAN);
    }
}
