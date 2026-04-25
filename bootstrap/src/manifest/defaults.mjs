const DEFAULT_INSTALL_MODE = "vendored";
const DEFAULT_PHASE = "discovery";

export function createManifest({
  projectName,
  projectType,
  primaryLanguage,
  cliVersion,
  skillsRepoVersion,
  skillsRepoSha,
  stack = [],
  phase = DEFAULT_PHASE,
  installMode = DEFAULT_INSTALL_MODE,
  compliance = {},
  activeSkills = [],
  activeAgents = [],
  hooks = {},
  owners = [],
  now = () => new Date(),
} = {}) {
  if (!projectName) throw new TypeError("createManifest: projectName required");
  if (!projectType) throw new TypeError("createManifest: projectType required");
  if (!primaryLanguage) throw new TypeError("createManifest: primaryLanguage required");
  if (!cliVersion) throw new TypeError("createManifest: cliVersion required");
  if (!skillsRepoVersion) throw new TypeError("createManifest: skillsRepoVersion required");

  const m = {
    $schema: "https://cure.dev/schemas/claude-manifest/v1.json",
    manifestVersion: 1,
    bootstrap: {
      cliVersion,
      skillsRepoVersion,
      lastAppliedAt: now().toISOString(),
      installMode,
    },
    project: {
      name: projectName,
      type: projectType,
      stack: [...stack],
      primaryLanguage,
      phase,
      owners: [...owners],
    },
    compliance: {
      hipaa: false,
      coppa: false,
      gdpr: false,
      pci: false,
      soc2: false,
      qsbs: false,
      ...compliance,
    },
    skills: {
      active: [...activeSkills],
      disabled: [],
      pinned: {},
    },
    agents: {
      active: [...activeAgents],
    },
    hooks: {
      preCommit: hooks.preCommit ?? [],
      postFeature: hooks.postFeature ?? [],
      prePR: hooks.prePR ?? [],
    },
    managedBlocks: {},
    vendored: {},
    customizations: {
      preserveFiles: ["CLAUDE.local.md", "STATE.local.md", ".claude/local/**"],
      templateOverrides: {},
    },
  };

  if (skillsRepoSha) m.bootstrap.skillsRepoSha = skillsRepoSha;
  return m;
}
