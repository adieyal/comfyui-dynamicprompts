from __future__ import annotations

import math
import subprocess
import sys
import types
from pathlib import Path

import pytest
from conftest import REPO_ROOT, folder_paths, set_wildcard_roots
from dynamicprompts.generators import CombinatorialPromptGenerator

import nodes
from nodes import wildcards as wildcards_module
from nodes.combinatorial import DPCombinatorialGenerator
from nodes.jinja import DPJinja
from nodes.magicprompt import DPMagicPrompt
from nodes.output_node import OutputString
from nodes.random import DPRandomGenerator

MANY_CHOICES = "{" + "|".join(f"option{i}" for i in range(50)) + "}"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_mappings_keep_keys_and_drop_feeling_lucky() -> None:
    expected = {
        "DPRandomGenerator",
        "DPCombinatorialGenerator",
        "DPJinja",
        "DPMagicPrompt",
        "DPOutput",
    }
    assert set(nodes.NODE_CLASS_MAPPINGS) == expected
    assert set(nodes.NODE_DISPLAY_NAME_MAPPINGS) == expected


@pytest.mark.parametrize(
    ("node", "names"),
    [
        (DPRandomGenerator, ["text", "seed", "autorefresh"]),
        (DPCombinatorialGenerator, ["text", "index"]),
        (DPMagicPrompt, ["text", "seed", "autorefresh"]),
        (DPJinja, ["text", "autorefresh"]),
        (OutputString, ["text"]),
    ],
)
def test_input_names_and_order(node: type, names: list[str]) -> None:
    assert list(node.INPUT_TYPES()["required"]) == names


def test_combinatorial_index_increments_by_default() -> None:
    index = DPCombinatorialGenerator.INPUT_TYPES()["required"]["index"]
    assert index[1]["control_after_generate"] == "increment"


def test_register_wildcard_folders() -> None:
    saved = folder_paths.folder_names_and_paths.pop("wildcards", None)
    try:
        wildcards_module.register_wildcard_folders()
        registered = folder_paths.get_folder_paths("wildcards")
    finally:
        if saved is not None:
            folder_paths.folder_names_and_paths["wildcards"] = saved
    assert registered == [
        str(Path(folder_paths.base_path) / "wildcards"),
        str(REPO_ROOT / "wildcards"),
    ]
    assert (REPO_ROOT / "wildcards").is_dir()


def test_random_seed_is_deterministic(wildcards: Path) -> None:
    node = DPRandomGenerator()
    first = node.get_prompt(MANY_CHOICES, 42, "No")
    assert node.get_prompt(MANY_CHOICES, 42, "No") == first
    others = {node.get_prompt(MANY_CHOICES, seed, "No")[0] for seed in range(10)}
    assert len(others) > 1


def test_random_large_seed(wildcards: Path) -> None:
    node = DPRandomGenerator()
    assert node.get_prompt(MANY_CHOICES, 0xFFFFFFFFFFFFFFFF, "No")[0].startswith(
        "option",
    )


def test_random_autorefresh_ignores_seed(wildcards: Path) -> None:
    node = DPRandomGenerator()
    prompts = {node.get_prompt(MANY_CHOICES, 1, "Yes")[0] for _ in range(10)}
    assert len(prompts) > 1


def test_node_instances_are_independent(wildcards: Path) -> None:
    a, b = DPRandomGenerator(), DPRandomGenerator()
    expected = a.get_prompt(MANY_CHOICES, 7, "No")
    b.get_prompt(MANY_CHOICES, 8, "No")
    b.get_prompt("{x|y}", 9, "No")
    assert a.get_prompt(MANY_CHOICES, 7, "No") == expected
    assert DPRandomGenerator().get_prompt(MANY_CHOICES, 7, "No") == expected


def test_is_changed(wildcards: Path) -> None:
    key = DPRandomGenerator.IS_CHANGED("a {b|c}", 1, "No")
    assert DPRandomGenerator.IS_CHANGED("a {b|c}", 1, "No") == key
    assert DPRandomGenerator.IS_CHANGED("a {b|c}", 2, "No") != key
    assert DPRandomGenerator.IS_CHANGED("a {b|d}", 1, "No") != key

    write(wildcards / "colors.txt", "red\n")
    after_add = DPRandomGenerator.IS_CHANGED("a {b|c}", 1, "No")
    assert after_add != key
    write(wildcards / "colors.txt", "red\nblue\n")
    assert DPRandomGenerator.IS_CHANGED("a {b|c}", 1, "No") != after_add

    assert math.isnan(DPRandomGenerator.IS_CHANGED("a {b|c}", 1, "Yes"))


def test_jinja_is_changed(wildcards: Path) -> None:
    key = DPJinja.IS_CHANGED("{{ 1 }}", "No")
    assert DPJinja.IS_CHANGED("{{ 1 }}", "No") == key
    assert DPJinja.IS_CHANGED("{{ 2 }}", "No") != key
    write(wildcards / "sub" / "x.txt", "x\n")
    assert DPJinja.IS_CHANGED("{{ 1 }}", "No") != key
    assert math.isnan(DPJinja.IS_CHANGED("{{ 1 }}", "Yes"))


@pytest.mark.parametrize(
    "node",
    [DPRandomGenerator, DPCombinatorialGenerator, DPMagicPrompt, DPJinja],
)
def test_save_to_metadata_inputs(node: type) -> None:
    inputs = node.INPUT_TYPES()
    assert list(inputs["optional"]) == ["save_to_metadata"]
    assert inputs["hidden"] == {
        "extra_pnginfo": "EXTRA_PNGINFO",
        "unique_id": "UNIQUE_ID",
    }


def test_save_to_metadata_writes_prompt(wildcards: Path) -> None:
    info: dict[str, object] = {"workflow": {}}
    (prompt,) = DPRandomGenerator().run("{red|blue}", 3, "No", "Yes", info, "5")
    (count_prompt, _) = DPCombinatorialGenerator().run("{a|b}", 1, "Yes", info, "6")
    (jinja,) = DPJinja().get_prompt("{{ 1 + 1 }}", "No", "Yes", info, "7")
    assert info["dynamicprompts"] == {"5": prompt, "6": count_prompt, "7": jinja}
    assert count_prompt == "b"
    assert jinja == "2"


def test_save_to_metadata_off_leaves_metadata_alone(wildcards: Path) -> None:
    info: dict[str, object] = {}
    DPRandomGenerator().run("{red|blue}", 3, "No", "No", info, "5")
    DPJinja().get_prompt("x", "No", "No", info, "7")
    assert info == {}


def test_save_to_metadata_without_metadata_warns(
    wildcards: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    assert DPRandomGenerator().run("red", 3, "No", "Yes", None, "5") == ("red",)
    assert "no image metadata" in caplog.text


def test_save_to_metadata_disables_caching(wildcards: Path) -> None:
    assert math.isnan(DPRandomGenerator.IS_CHANGED("a", 1, "No", "Yes", None, "5"))
    assert math.isnan(DPJinja.IS_CHANGED("a", "No", "Yes", None, "7"))
    assert isinstance(DPRandomGenerator.IS_CHANGED("a", 1, "No", "No", None, "5"), str)
    assert math.isnan(DPCombinatorialGenerator.IS_CHANGED("a", 1, "Yes", None, "6"))


def test_combinatorial_is_changed(wildcards: Path) -> None:
    key = DPCombinatorialGenerator.IS_CHANGED("a {b|c}", 1)
    assert DPCombinatorialGenerator.IS_CHANGED("a {b|c}", 1, "No", None, "6") == key
    assert DPCombinatorialGenerator.IS_CHANGED("a {b|c}", 2) != key
    assert DPCombinatorialGenerator.IS_CHANGED("a {b|d}", 1) != key


def test_combinatorial_index_and_count(wildcards: Path) -> None:
    """[REQ BATCH.COUNT]"""
    node = DPCombinatorialGenerator()
    assert DPCombinatorialGenerator.RETURN_TYPES == ("STRING", "INT")
    assert node.get_prompt("{a|b|c}", 0) == ("a", 3)
    assert node.get_prompt("{a|b|c}", 2) == ("c", 3)
    assert node.get_prompt("{a|b|c}", 4) == ("b", 3)
    assert node.get_prompt("{a|b} {x|y}", 0)[1] == 4


def test_combinatorial_large_count_is_exact_and_index_wraps(wildcards: Path) -> None:
    """[REQ BATCH.COUNT]"""
    four = "{a|b|c|d}"
    template = " ".join([four] * 8)  # 4**8 = 65,536 combinations
    index = 50_000 + 65_536  # index % count = 50,000 > 10,000
    prompt, count = DPCombinatorialGenerator().get_prompt(template, index)
    assert count == 65_536
    generator = CombinatorialPromptGenerator(
        wildcards_module.get_wildcard_manager(), seed=index
    )
    assert prompt == generator.prompt_at(template, index % count)


def test_combinatorial_index_fixes_random_choices(wildcards: Path) -> None:
    """[SCENARIO SC15@1]"""
    template = "{~a|b|c|d|e|f|g|h} {x|y}"
    node = DPCombinatorialGenerator()
    first = node.get_prompt(template, 4)
    assert all(node.get_prompt(template, 4) == first for _ in range(5))


def test_combinatorial_later_pass_keeps_combination_with_fresh_random_parts(
    wildcards: Path,
) -> None:
    """[SCENARIO SC15@1]"""
    template = MANY_CHOICES.replace("{", "{~", 1) + " {x|y}"
    node = DPCombinatorialGenerator()
    first, count = node.get_prompt(template, 1)
    assert count == 2
    later = [node.get_prompt(template, 1 + count * n)[0] for n in range(1, 11)]
    assert all(prompt.endswith(" y") for prompt in [first, *later])
    assert len({first, *later}) > 1


def test_combinatorial_count_above_old_cap_passes_through(wildcards: Path) -> None:
    """[REQ BATCH.COUNT]"""
    ten = "{0|1|2|3|4|5|6|7|8|9}"
    template = " ".join([ten] * 12)  # 10**12 combinations
    prompt, count = DPCombinatorialGenerator().get_prompt(template, 7)
    assert count == 10**12
    generator = CombinatorialPromptGenerator(
        wildcards_module.get_wildcard_manager(), seed=7
    )
    assert prompt == generator.prompt_at(template, 7)


def test_combinatorial_index_wraps(wildcards: Path) -> None:
    """[REQ BATCH.COUNT]"""
    # 3 random choices (counted as 1) * 2**5 * 5**4 = 20,000 combinations
    template = "{~p|q|r} " + " ".join(["{a|b}"] * 5 + ["{1|2|3|4|5}"] * 4)
    node = DPCombinatorialGenerator()
    for index, position in [(20_005, 5), (19_999, 19_999)]:
        prompt, count = node.get_prompt(template, index)
        assert count == 20_000
        generator = CombinatorialPromptGenerator(
            wildcards_module.get_wildcard_manager(), seed=index
        )
        assert prompt == generator.prompt_at(template, position)


def test_combinatorial_unbounded_raises(wildcards: Path) -> None:
    """[REQ BATCH.COUNT]"""
    write(wildcards / "rec.txt", "__rec__\n")
    with pytest.raises(ValueError, match="recursive wildcard.*unbounded"):
        DPCombinatorialGenerator().get_prompt("__rec__", 1)


def test_combinatorial_characters_times_outfits_cover_every_pair(
    wildcards: Path,
) -> None:
    """[SCENARIO SC6@2]"""
    template = "{Mira|Ash} in a {blue coat|red coat|green coat}"
    node = DPCombinatorialGenerator()
    results = [node.get_prompt(template, index) for index in range(6)]
    prompts = [prompt for prompt, _ in results]
    assert [count for _, count in results] == [6] * 6
    assert len(set(prompts)) == 6
    assert set(prompts) == {
        f"{character} in a {outfit}"
        for character in ("Mira", "Ash")
        for outfit in ("blue coat", "red coat", "green coat")
    }
    assert node.get_prompt(template, 3) == results[3]


def test_combinatorial_unbounded_raises_and_two_combinations_cycle(
    wildcards: Path,
) -> None:
    """[SCENARIO SC7@2]"""
    write(wildcards / "rec.txt", "__rec__\n")
    node = DPCombinatorialGenerator()
    with pytest.raises(ValueError, match="unbounded"):
        node.get_prompt("__rec__", 1)
    first, count = node.get_prompt("{a|b}", 0)
    assert count == 2
    assert node.get_prompt("{a|b}", 1)[0] != first
    assert node.get_prompt("{a|b}", 2)[0] == first


def test_combinatorial_duplicates_weight_and_missing_wildcard_is_one_combination(
    wildcards: Path,
) -> None:
    """[SCENARIO SC16@1]"""
    write(wildcards / "pets.txt", "cat\ndog\ncat\n")
    node = DPCombinatorialGenerator()

    count = node.get_prompt("{red|red|blue}", 0)[1]
    assert count == 3
    variants = [node.get_prompt("{red|red|blue}", index)[0] for index in range(count)]
    assert sorted(variants) == ["blue", "red", "red"]

    count = node.get_prompt("__pets__", 0)[1]
    assert count == 3
    lines = [node.get_prompt("__pets__", index)[0] for index in range(count)]
    assert sorted(lines) == ["cat", "cat", "dog"]

    assert node.get_prompt("__nope__", 0) == ("__nope__", 1)


def test_random_keeps_duplicate_variant_options(wildcards: Path) -> None:
    """[REQ COMPAT.DUPLICATES]"""
    node = DPRandomGenerator()
    seeds = range(900)
    reds = sum(node.get_prompt("{red|red|blue}", s, "No")[0] == "red" for s in seeds)
    # 2/3 expected with duplicates kept; 1/2 if they were dropped.
    assert 0.58 < reds / len(seeds) < 0.75


def test_combinatorial_missing_wildcard_inside_variant_is_one_option(
    wildcards: Path,
) -> None:
    """[REQ COMPAT.DUPLICATES]"""
    node = DPCombinatorialGenerator()
    count = node.get_prompt("{a|__nope__}", 0)[1]
    assert count == 2
    prompts = {node.get_prompt("{a|__nope__}", index)[0] for index in range(count)}
    assert prompts == {"a", "__nope__"}


@pytest.mark.parametrize("template", ["{~a|b}", "{@a|b}"])
def test_combinatorial_lone_random_or_cyclic_part_counts_once(
    wildcards: Path,
    template: str,
) -> None:
    """[REQ COMPAT.DUPLICATES]"""
    node = DPCombinatorialGenerator()
    prompt, count = node.get_prompt(template, 0)
    assert count == 1
    assert prompt in {"a", "b"}


def test_combinatorial_zero_count_returns_empty(
    wildcards: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """[REQ BATCH.COUNT]"""
    assert DPCombinatorialGenerator().get_prompt("", 1) == ("", 0)
    assert "no combinations" in caplog.text


def test_wildcard_edit_picked_up(wildcards: Path) -> None:
    node = DPRandomGenerator()
    write(wildcards / "animal.txt", "cat\n")
    assert node.get_prompt("__animal__", 1, "No") == ("cat",)
    write(wildcards / "animal.txt", "giraffe\n")
    assert node.get_prompt("__animal__", 1, "No") == ("giraffe",)
    write(wildcards / "plant.txt", "fern\n")
    assert node.get_prompt("__plant__", 1, "No") == ("fern",)


def test_multiple_wildcard_roots(tmp_path: Path) -> None:
    first, second = tmp_path / "one", tmp_path / "two"
    write(first / "animal.txt", "cat\n")
    write(second / "nested" / "plant.txt", "fern\n")
    set_wildcard_roots(first, second, tmp_path / "missing")
    node = DPCombinatorialGenerator()
    assert node.get_prompt("__animal__ __nested/plant__", 0) == (
        "cat fern",
        1,
    )


def test_jinja_wildcard(wildcards: Path) -> None:
    write(wildcards / "colors.txt", "red\nblue\n")
    result = DPJinja().get_prompt('{{ wildcard("colors") | join(",") }}', "No")
    assert result == ("blue,red",)


def test_jinja_includes_templates_from_every_wildcard_folder(tmp_path: Path) -> None:
    first, second = tmp_path / "first", tmp_path / "second"
    write(first / "a.jinja", "from first")
    write(second / "b.jinja", "from second")
    set_wildcard_roots(first, second)
    template = "{% include 'a.jinja' %}, {% include 'b.jinja' %}"
    assert DPJinja().get_prompt(template, "No") == ("from first, from second",)


def test_output_string() -> None:
    assert OutputString().output_string(text="hello") == {"ui": {"text": ["hello"]}}
    assert OutputString.OUTPUT_NODE is True
    assert OutputString.DEPRECATED is True


def test_magicprompt_seeded_with_fake_generator(
    wildcards: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int | None] = []

    class FakeMagicPromptGenerator:
        def __init__(self, prompt_generator: object, seed: int | None) -> None:
            calls.append(seed)
            self._inner = prompt_generator

        def generate(self, text: str, num: int) -> list[str]:
            return [f"{self._inner.generate(text, num)[0]}, magic"]  # type: ignore[attr-defined]

    fake = types.ModuleType("dynamicprompts.generators.magicprompt")
    fake.MagicPromptGenerator = FakeMagicPromptGenerator  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "dynamicprompts.generators.magicprompt", fake)

    node = DPMagicPrompt()
    first = node.get_prompt(MANY_CHOICES, 2**32 + 5, "No")
    assert first == node.get_prompt(MANY_CHOICES, 2**32 + 5, "No")
    assert first[0].endswith(", magic")
    node.get_prompt(MANY_CHOICES, 3, "Yes")
    assert calls == [5, 5, None]


def test_magicprompt_failure_raises(
    wildcards: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "dynamicprompts.generators.magicprompt", None)
    with pytest.raises(ImportError):
        DPMagicPrompt().get_prompt("a cat", 1, "No")


def test_random_empty_text(wildcards: Path) -> None:
    assert DPRandomGenerator().get_prompt("", 0, "No") == ("",)


def test_yaml_wildcards(wildcards: Path) -> None:
    write(wildcards / "pack.yaml", "animal:\n  - cat\n")
    assert DPRandomGenerator().get_prompt("__animal__", 0, "No") == ("cat",)


def test_import_does_not_import_transformers(tmp_path: Path) -> None:
    script = f"""
import sys, types
sys.modules["transformers"] = None  # any import of transformers now fails
fp = types.ModuleType("folder_paths")
fp.base_path = {str(tmp_path)!r}
store = {{}}
fp.add_model_folder_path = lambda n, p, is_default=False: store.setdefault(n, []).append(p)
fp.get_folder_paths = lambda n: list(store.get(n, []))
sys.modules["folder_paths"] = fp
sys.path.insert(0, {str(REPO_ROOT)!r})
import nodes
assert "dynamicprompts.generators.magicprompt" not in sys.modules
print(sorted(nodes.NODE_CLASS_MAPPINGS))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "DPMagicPrompt" in result.stdout
