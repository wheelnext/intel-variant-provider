# Intel Variant Provider Plugin

A variant provider plugin for the Wheel Variant upcoming [proposed standard][PEP XXX]
that enables automatic detection and selection of Intel GPU-optimized Python packages.
This plugin is part of the [WheelNext] initiative to "Re-invent the Wheel" and Python
package distribution for scientific and hardware-accelerated computing.

## Compatibility with package managers

> [!IMPORTANT]
> This plugin implements support for the specification which is a _work in progress_ and
> is not intended for production use. It is provided as-is, without guarantees or warranties,
> and may change, disappear, or stop working at any time.
>
> There is no backward compatibility guarantees for the components implementing the [proposed
> specification][PEP XXX]. Be careful selecting component versions. Below we outline tested
> combinations of components which are known to work.

At the moment packaging of the wheel variants and queries of the plugins list and their
metadata is supported by the [variantlib] library. Intel Variant Provider Plugin is currently
validated with the following version of variantlib:
* https://github.com/wheelnext/variantlib/commit/75bea8ef4886d5fd4d5282ee5ba6b45f48badd70

Package manager which supports proposed specification is needed to install variant wheels.
The patched version of `pip` can be found here:
* https://github.com/wheelnext/pep_xxx_wheel_variants/tree/e44bf06c26872be158949f93fecb0c8ee762653e/pep_xxx_wheel_variants

The patched version of `uv` can be found here:
* https://github.com/astral-sh/uv/pull/12203

Note that current efforts are focused on `uv`. Patches for `pip` are supported with the
best efforts. Run the following to install compatible version of `uv`:

* On Linux:

```
curl -LsSf https://astral.sh/uv/install.sh | INSTALLER_DOWNLOAD_URL=https://wheelnext.astral.sh/v0.0.2 sh
```

* On Windows:

```
powershell -c { $env:INSTALLER_DOWNLOAD_URL = 'https://wheelnext.astral.sh/v0.0.2'; irm https://astral.sh/uv/install.ps1 | iex }
```

## Detected Hardware Properties

* GPU Architecture (Compute Capability)

   * Determines the compute capability available on the system.
   * Resolves with compute capability compatibility in mind.
   * Returns feature list in the form of `intel::device_ip::<ip>`
   * Each value (`<ip>`) in the list represents human readable form of
     Intel hardware device IP (GMDID) quariable via Level Zero [ZE_extension_device_ip_version]

## WheelNext package index

[WheelNext] initiative supports aggregated index of the packages which are enabled with variant providers.

* Release index:
  * https://wheelnext.github.io/variants-index/

* Test index:
  * https://wheelnext.github.io/variants-index-test/

The WheelNext version of `uv` is configured to works with the release index from above.

## Configuring Your Project

Add variant configuration to your `pyproject.toml`:

```
[variant.default-priorities]
namespace = ["intel"]

[variant.providers.intel]
requires = ["intel_variant_provider"]
enable-if = "platform_system == 'Linux'"
plugin-api = "intel_variant_provider.plugin:IntelVariantPlugin"
```

## Understanding Intel Device IP Values

Device IP is an identifier (GMDID) assigned to differentiate architectures of
compute platforms of Intel GPU devices. Few different Intel GPU devices (with
the different device IDs) might be built on the same compute platform.

Programmatically device IP can be queried for each Intel GPU device using
Level Zero [ZE_extension_device_ip_version] API. Returned value format is
Intel specific and requires conversion to human readable form.

Intel offline compiler (`ocloc`) generates code for one or few target compute
platforms passed in `-device <device_type>` argument. Each `<device type>` in
the list can be set as Device IP or via acronym name internally mapped to the
respective Device IP. To query Device IP(s) for the specific acronym
`ocloc ids` command can be used. For example:

```
$ ocloc ids bmg
Matched ids:
20.1.0

$ ocloc ids xe3
Matched ids:
30.0.0
30.0.4
30.1.0
30.1.1
```

For Python package to target specific Intel architectures using XPU variant
provider plugin, it's required to build package variants for these
architectures and set `intel::device_ip::<ip>` properties accordingly. For the
above example of `bmg` and `xe3` that would be:

```
# for bmg variant:
intel::device_ip::20.1.0

# for xe3 variant:
intel::device_ip::30.0.0
intel::device_ip::30.0.4
intel::device_ip::30.1.0
intel::device_ip::30.1.1
```

## License

This project is licensed under the Apache 2 License - see the [LICENSE](LICENSE) file for details.

[ZE_extension_device_ip_version]: https://oneapi-src.github.io/level-zero-spec/level-zero/latest/core/EXT_DeviceIpVersion.html#ze-extension-device-ip-version

[variantlib]: https://github.com/wheelnext/variantlib
[WheelNext]: https://wheelnext.dev/
[PEP XXX]: https://wheelnext.dev/proposals/pepxxx_wheel_variant_support/
