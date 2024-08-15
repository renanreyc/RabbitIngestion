# ncs-ingestion



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/neogrid1/data-platform/data-engineering/ncs-ingestion.git
git branch -M main
git push -uf origin main
```

# Diagrama construido com mermaid tool:
:::mermaid
    flowchart LR

        classDef orange fill:orange,stroke:#E65729,stroke-width:2px,color:#000000
        classDef purple fill:purple,stroke:purple,stroke-width:2px,color#fff
        classDef grey fill:grey,stroke:#fff,stroke-width:2px,color:#fff
        classDef blue fill:navy,stroke:#fff,stroke-width:2px,color:#fff

        NCS{{NCS \n API}}:::grey
        USER((USER)):::blue
        PRX{{PROXY}}:::grey    

        subgraph RMQ["RabbitMQ"]
                direction LR
                EXG[Exchanges]
                Q[Queue]

                
        end     
            USER -.->|upload new file| PRX 
            PRX -.->|publish \n message| EXG
            PRX -->|load data| NCS
            
            EXG -.->|"(n) to (1)"| Q
            Q <-.->|read \n message| CNF
            
        subgraph "Dataplatform NDP Ingestion" 
            direction LR
            CNF{CHECK \n NEW FILE}:::orange

            subgraph INGESTION
                direction BT
                RM[Read \n Metadata]
                DF[Download \n NCS file]
                CF[Convert \n File]
                SF[Send \n File]

                RM -.-> DF
                DF --> CF
                CF --> SF
            end        
        end
        
        subgraph OBS["Object Storage Server (OBS)"]
        direction LR
            DVV[(DPVISIBILIDADEVAREJO)]:::grey    
        end

            CNF -.->|trigger \n + metadata| RM
            NCS -->|binary \n data| DF
            SF -->|upload \n new file| DVV
:::