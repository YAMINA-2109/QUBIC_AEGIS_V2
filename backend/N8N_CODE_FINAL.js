const inputData = $input.item.json;

const riskScore = inputData.risk_score || inputData.body?.risk_score || 0;
const attackType = inputData.type || inputData.body?.type || "Unknown Type";
const analysis =
  inputData.analysis ||
  inputData.body?.analysis ||
  "No detailed analysis provided.";

const embed = {
  title: `⚠️ ${attackType}`,
  color: riskScore >= 95 ? 15548997 : riskScore >= 80 ? 16753920 : 3447003,
  fields: [
    {
      name: "🔥 Risk Score",
      value: `${riskScore} / 100`,
      inline: true,
    },
    {
      name: "👁️ Attack Type",
      value: attackType,
      inline: true,
    },
    {
      name: "🧠 AI Analysis",
      value:
        analysis.length > 1000 ? analysis.substring(0, 1000) + "..." : analysis,
      inline: false,
    },
  ],
  footer: {
    text: "Aegis Automated Defense",
  },
  timestamp: new Date().toISOString(),
};

return {
  json: {
    content: "🚨 **QUBIC AEGIS ALERT SYSTEM**",
    embeds: [embed],
  },
};
