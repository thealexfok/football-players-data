library(rvest)
library(tidyverse)
library(data.table)

URL <- "https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1"
URL = url(URL, "rb")
WS <- read_html(URL)
close(URL)
URLs <- WS %>% html_nodes("#yw1 .no-border-links a:nth-child(1)") %>% html_attr("href") %>% as.character()
URLs <- paste0("https://www.transfermarkt.com",URLs)
Catcher1 <- data.frame(Player=character(),P_URL=character())

for (i in URLs) {
  url = url(i, "rb")
  WS1 <- read_html(url)
  close(url)
  Player <- WS1 %>% html_nodes(".nowrap a") %>% html_text() %>% as.character()
  P_URL <- WS1 %>% html_nodes(".nowrap a") %>%  html_attr("href") %>% as.character()
  temp <- data.frame(Player,P_URL)
  Catcher1 <- rbind(Catcher1,temp)
  cat("*")
}

no.of.rows <- nrow(Catcher1)
odd_indexes <- seq(1,no.of.rows,2)
Catcher1 <- data.frame(Catcher1[odd_indexes,])
Catcher1$P_URL <- paste0("https://transfermarkt.com", Catcher1$P_URL)

Catcher2 <- data.frame(Name=character(), Value=character(), Position=character(), Age=character(), Nat=character(), Endcontract=character())
loop_index_1 <- 0
for (i in Catcher1$P_URL[1:10]){
  loop_index_1 <- loop_index_1 + 1
  url = url(i, "rb")
  WS2 <- read_html(url)
  close(url)
  Name <- Catcher1$Player[loop_index_1]
  Value <- WS2 %>% html_nodes(".tm-player-market-value-development__current-value") %>% html_text() %>% as.character()
  Position <- WS2 %>% html_nodes(".data-header__items+ .data-header__items .data-header__label:nth-child(2) span") %>% html_text() %>% as.character()
  for (j in 1:30){
    templink = paste0(".info-table__content--regular:nth-child(",j,")")
    tempage <- WS2 %>% html_nodes(templink)%>% html_text() %>% as.character()
    if (length(tempage) != 0){
      if((tempage== "Age:")){
        Age <- WS2 %>% html_nodes(paste0(".info-table__content--bold:nth-child(",j+1,")"))%>% html_text() %>% as.character()
        break
      }}}
  Nat <- WS2 %>% html_nodes(".flagge+ a") %>% html_text() %>% as.character()
  for (j in 1:30){
    templink = paste0(".info-table__content--regular:nth-child(",j,")")
    tempcon <- WS2 %>% html_nodes(templink)%>% html_text() %>% as.character()
    if (length(tempcon) != 0){
      if((tempcon== "Contract expires:")){
        Endcontract <- WS2 %>% html_nodes(paste0(".info-table__content--bold:nth-child(",j+1,")"))%>% html_text() %>% as.character()
        break
      }}}
  if ((length(Name) > 0) & (length(Value) > 0) & (length(Position) > 0) & (length(Age) > 0) & (length(Nat) > 0) & (length(Endcontract) > 0) ) {
    temp2 <- data.frame(Name, Value, Position, Age, Nat, Endcontract)
    Catcher2 <- rbind(Catcher2,temp2)
  }
  
  cat("*")
}

Catcher2map <- Catcher2 %>% 
  mutate(Value = gsub(" ", "", Value), Value = substr(Value, 3, nchar(Value)))%>% 
  mutate(Position = gsub(" ", "", Position), Position = substr(Position, 2, nchar(Position)))

fwrite(Catcher2map,"D:/Projects/Soccer_MV_App/Bundesliga.csv",append = TRUE,na= "X",showProgress=getOption("datatable.showProgress", interactive()))

