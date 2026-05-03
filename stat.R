library(weights)

df <- read.csv("stat.csv")
colnames(df) <- c("시즌", "데미지", "마력", "방무", "크뎀", "벞지", "소환수")

current.season <- max(df$시즌) # 과거 시즌 적용 시 해당 변수 수정
wt <- ifelse(df$시즌 > current.season, 0, 2 ^ (df$시즌 - current.season))


wtd.hist(df$데미지, seq(700, 950, 10), xlab = "데미지",
         weight = wt, col = "#D3D3D3", ylab = "도수", main = "", cex.lab = 1.5)
데미지 <- wtd.median(df$데미지, wt)
abline(v = 데미지, lwd = 3)

wtd.hist(df$마력, breaks = seq(110, 210, 5), xlab = "마력%",
         weight = wt, col = "#D3D3D3", ylab = "도수", main = "", cex.lab = 1.5)
마력 <- wtd.median(df$마력, wt)
abline(v = 마력, lwd = 3)
axis(1, seq(110, 210, 20))

wtd.hist(df$방무, breaks = seq(97.5, 100, 0.1), xlab = "방어율 무시",
         weight = wt, col = "#D3D3D3", ylab = "도수", main = "", cex.lab = 1.5)
방무 <- wtd.median(df$방무, wt)
abline(v = 방무, lwd = 3)

wtd.hist(df$크뎀, breaks = seq(140, 200, 2), xlab = "크리티컬 데미지",
         weight = wt, col = "#D3D3D3", ylab = "도수", main = "", cex.lab = 1.5)
크뎀 <- wtd.median(df$크뎀, wt)
abline(v = 크뎀, lwd = 3)

wtd.hist(df$벞지, breaks = seq(40, 110, 5), xlab = "버프 지속시간 증가",
         weight = wt, col = "#D3D3D3", ylab = "도수", main = "", cex.lab = 1.5)
벞지 <- wtd.median(df$벞지, wt)
abline(v = 벞지, lwd = 3)

# 짝수 단위로만 표시되므로 x축 위치 조정
wtd.hist(df$소환수 + 1, breaks = seq(19, 43, 2), axes = F, xlab = "소환수 지속시간 증가",
         weight = wt, col = "#D3D3D3", ylab = "도수", main = "", cex.lab = 1.5)
소환수 <- wtd.median(df$소환수, wt)
abline(v = 소환수, lwd = 3)
axis(1, seq(20, 42, 2))
axis(2, seq(0, 30, 5))

# 결과 출력
{
  cat("PERIOD_NO = ", current.season, '\n', sep = "")
  cat('\n')
  cat("# 고정 스펙\n")
  cat("dR = ", 데미지, " # 데미지, 보스 데미지, 상추뎀\n", sep = "")
  cat("madR = ", 마력, '\n', sep = "")
  cat("mobpdpR = 3.8 * ", 1 - 방무 / 100, " # ", 방무, "%\n", sep = "")
  cat("criticalDamage = ", 크뎀, '\n', sep = "")
  cat("bufftimeR = ", 벞지, '\n', sep = "")
  cat("summonTimeR = ", 소환수, '\n', sep = "")
}