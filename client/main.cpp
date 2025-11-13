#include <algorithm>
#include <array>
#include <cstring>
#include <memory>
#include <random>
#include <span>
#include <string>

#include "xatmi.h"

std::mt19937_64 rng;

auto create_buffer(std::span<const std::byte> payload)
{
    auto buffer = std::unique_ptr<char, decltype(&::tpfree)>(tpalloc(CASUAL_BUFFER_JSON_TYPE, 0, payload.size_bytes()), &::tpfree);
    std::memcpy(buffer.get(), payload.data(), payload.size_bytes());
    return buffer;
}

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

int main(int argc, char *argv[])
{
    auto num_calls = 1000;
    const auto payload_size = 1024;
    auto service = "casual/example/echo";

    std::array<std::mt19937_64::result_type, payload_size / sizeof(std::mt19937_64::result_type)> payload;
    std::ranges::generate_n(payload.begin(), payload.size(), rng);

    for (int i = 0; i < num_calls; ++i)
    {
        auto response = service_call( service, std::as_bytes(std::span(payload)), TPNOTRAN);
    }
}
